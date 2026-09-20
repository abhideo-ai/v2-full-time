-- db/operations/clone_seat_resume.sql
--
-- Start a PER-SEAT résumé as a SELECTION WITH EDITS off the master, never as a copied
-- file. This is an OPERATION, not a migration: it runs once per new seat, for the rest
-- of the search.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
--        set_config('clone.slug','<slug>',false)" -f db/operations/clone_seat_resume.sql
--
-- It creates doc_key 'seat:<slug>' in resume_documents / resume_sections / resume_blocks
-- by copying every master row verbatim. The Rule 7 re-vectoring is then applied as
-- UPDATEs against the seat's rows only -- the master is never touched.
--
-- Why this exists as a file: CLAUDE.md fixes that all SQL in this repo lives in db/ so
-- every data change is re-runnable and verifiable later. The Nexifyr seat document was
-- created ad hoc and left no record of how, which is exactly the gap this closes.
--
-- ⛔ REFUSES to touch a seat whose application has already been SENT. A sent résumé is
-- history: re-cloning one would silently replace the document a recruiter is holding.
-- ⛔ REFUSES to overwrite an existing seat document. Drop it deliberately, or edit it.
-- ⛔ REFUSES if the master is empty, rather than creating a hollow seat document.

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    v_slug    text := current_setting('clone.slug', true);
    v_doc     text;
    v_status  text;
    v_master  integer;
    v_copied  integer;
BEGIN
    IF v_slug IS NULL OR btrim(v_slug) = '' THEN
        RAISE EXCEPTION 'clone.slug is required -- name the seat explicitly';
    END IF;

    v_doc := 'seat:' || v_slug;

    SELECT status::text INTO v_status FROM applications WHERE slug = v_slug;
    IF v_status IS NULL THEN
        RAISE EXCEPTION 'no application with slug % -- run resume.py new first', v_slug;
    END IF;

    -- A sent résumé is history. Migration 011 guards resume_version_bullets; the .docx
    -- path runs through resume_blocks, so the same freeze has to be stated here too.
    IF v_status IN ('applied', 'heard_back', 'not_selected', 'withdrawn') THEN
        RAISE EXCEPTION
          'REFUSING: % is already % -- a sent résumé is never regenerated', v_slug, v_status;
    END IF;

    IF EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_doc) THEN
        RAISE EXCEPTION
          'REFUSING: % already exists -- edit it, or delete it deliberately first', v_doc;
    END IF;

    SELECT count(*) INTO v_master
      FROM resume_blocks WHERE doc_key = 'master' AND retired_at IS NULL;
    IF v_master = 0 THEN
        RAISE EXCEPTION 'REFUSING: master carries no blocks -- load it before cloning';
    END IF;

    INSERT INTO resume_documents
    SELECT v_doc, title, lang, stylesheet_href, favicon_href, script_src,
           contract_comment, intro_html, dates_heading, education_label,
           education_note_html, personal_heading, personal_note_html, now()
      FROM resume_documents WHERE doc_key = 'master';

    -- Roles, education, certifications and profile are doc-scoped too, and
    -- resume_sections.role_n has a foreign key onto resume_roles -- so roles must
    -- land BEFORE sections or the insert fails.
    INSERT INTO resume_roles (doc_key, n, company, role_title, date_from, date_to,
                              location, date_to_emphasised)
    SELECT v_doc, n, company, role_title, date_from, date_to, location, date_to_emphasised
      FROM resume_roles WHERE doc_key = 'master';

    INSERT INTO resume_education (doc_key, ord, credential, institution,
                                  date_range, is_highest)
    SELECT v_doc, ord, credential, institution, date_range, is_highest
      FROM resume_education WHERE doc_key = 'master';

    INSERT INTO resume_certifications (doc_key, ord, name, issuer, awarded,
                                       card_only, note)
    SELECT v_doc, ord, name, issuer, awarded, card_only, note
      FROM resume_certifications WHERE doc_key = 'master';

    -- value_text is a generated column; never insert into it.
    INSERT INTO resume_profile (doc_key, ord, field_label, value_html)
    SELECT v_doc, ord, field_label, value_html
      FROM resume_profile WHERE doc_key = 'master';

    INSERT INTO resume_sections (doc_key, ord, section_id, section_kind,
                                 heading_html, card_only, role_n)
    SELECT v_doc, ord, section_id, section_kind, heading_html, card_only, role_n
      FROM resume_sections WHERE doc_key = 'master';

    INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord,
                               bullet_key, html, retired_at, created_at)
    SELECT v_doc, section_id, section_kind, ord, bullet_key, html, NULL, now()
      FROM resume_blocks WHERE doc_key = 'master' AND retired_at IS NULL;

    GET DIAGNOSTICS v_copied = ROW_COUNT;

    IF v_copied <> v_master THEN
        RAISE EXCEPTION 'REFUSING: copied % of % master blocks', v_copied, v_master;
    END IF;

    RAISE NOTICE 'OK - % created from master: % blocks', v_doc, v_copied;
END $$;

COMMIT;
