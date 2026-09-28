-- db/operations/clone_master_variant.sql
--
-- Copy the master résumé, row for row, into a DRAFT VARIANT: doc_key 'variant:<name>'.
-- A variant is an alternative telling of the whole master (for example the story-cluster
-- draft of 28 Sep 2026), edited in its own rows and generated to its own .docx. The
-- master is never touched.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
--        set_config('variant.name','story-clusters',false)" -f db/operations/clone_master_variant.sql
--
-- The sibling of clone_seat_resume.sql, which copies the master into 'seat:<slug>' for one
-- application and refuses seats already sent. A variant belongs to no application, so
-- that check does not apply.
--
-- ⛔ REFUSES to overwrite an existing variant. Delete it deliberately, or edit it.
-- ⛔ REFUSES if the master is empty.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_name   text := current_setting('variant.name', true);
    v_doc    text;
    v_master integer;
    v_copied integer;
BEGIN
    IF v_name IS NULL OR v_name !~ '^[a-z0-9]+(-[a-z0-9]+)*$' THEN
        RAISE EXCEPTION 'variant.name is required: lowercase words joined by hyphens';
    END IF;
    v_doc := 'variant:' || v_name;

    IF EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_doc) THEN
        RAISE EXCEPTION 'REFUSING: % already exists -- edit it, or delete it deliberately first', v_doc;
    END IF;

    SELECT count(*) INTO v_master FROM resume_blocks WHERE doc_key = 'master' AND retired_at IS NULL;
    IF v_master = 0 THEN
        RAISE EXCEPTION 'REFUSING: master carries no blocks -- load it before cloning';
    END IF;

    INSERT INTO resume_documents
    SELECT v_doc, title, lang, stylesheet_href, favicon_href, script_src,
           contract_comment, intro_html, dates_heading, education_label,
           education_note_html, personal_heading, personal_note_html, now()
      FROM resume_documents WHERE doc_key = 'master';

    -- Roles before sections: resume_sections.role_n has a foreign key onto resume_roles.
    INSERT INTO resume_roles (doc_key, n, company, role_title, date_from, date_to,
                              location, date_to_emphasised)
    SELECT v_doc, n, company, role_title, date_from, date_to, location, date_to_emphasised
      FROM resume_roles WHERE doc_key = 'master';

    INSERT INTO resume_education (doc_key, ord, credential, institution, date_range, is_highest)
    SELECT v_doc, ord, credential, institution, date_range, is_highest
      FROM resume_education WHERE doc_key = 'master';

    INSERT INTO resume_certifications (doc_key, ord, name, issuer, awarded, card_only, note)
    SELECT v_doc, ord, name, issuer, awarded, card_only, note
      FROM resume_certifications WHERE doc_key = 'master';

    -- value_text is a generated column; never insert into it.
    INSERT INTO resume_profile (doc_key, ord, field_label, value_html)
    SELECT v_doc, ord, field_label, value_html FROM resume_profile WHERE doc_key = 'master';

    INSERT INTO resume_sections (doc_key, ord, section_id, section_kind, heading_html, card_only, role_n)
    SELECT v_doc, ord, section_id, section_kind, heading_html, card_only, role_n
      FROM resume_sections WHERE doc_key = 'master';

    INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html, retired_at, created_at)
    SELECT v_doc, section_id, section_kind, ord, bullet_key, html, NULL, now()
      FROM resume_blocks WHERE doc_key = 'master' AND retired_at IS NULL;

    GET DIAGNOSTICS v_copied = ROW_COUNT;
    IF v_copied <> v_master THEN
        RAISE EXCEPTION 'REFUSING: copied % of % master blocks', v_copied, v_master;
    END IF;

    RAISE NOTICE 'OK - % created from master: % blocks', v_doc, v_copied;
END $$;

COMMIT;
