-- db/operations/promote_variant_to_master.sql
--
-- Make a DRAFT VARIANT the master résumé. An OPERATION, run only when he says so
-- (the story-cluster draft: "make it master", 29 Sep 2026).
--
--   1. back up the master first:
--      psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('variant.name','master-2026-09-29',false)" -f db/operations/clone_master_variant.sql
--   2. then promote:
--      psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('promote.variant','story-clusters',false), set_config('promote.backup','master-2026-09-29',false)" -f db/operations/promote_variant_to_master.sql
--
-- Only the bullets (resume_blocks) are replaced. It refuses unless the variant's sections match
-- the master's exactly (a variant is a re-telling, not a re-structuring), and unless the backup
-- exists and holds every live master bullet word for word. Seat résumés (seat:<slug>) are
-- separate copies, so sent seats are unaffected.

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    v_var    text := 'variant:' || current_setting('promote.variant', true);
    v_bak    text := 'variant:' || current_setting('promote.backup', true);
    v_n      integer;
    v_diff   integer;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_var) THEN
        RAISE EXCEPTION 'REFUSING: % does not exist', v_var;
    END IF;

    SELECT count(*) INTO v_diff FROM (
        (SELECT section_id, section_kind, ord FROM resume_sections WHERE doc_key = 'master'
         EXCEPT SELECT section_id, section_kind, ord FROM resume_sections WHERE doc_key = v_var)
        UNION ALL
        (SELECT section_id, section_kind, ord FROM resume_sections WHERE doc_key = v_var
         EXCEPT SELECT section_id, section_kind, ord FROM resume_sections WHERE doc_key = 'master')) d;
    IF v_diff <> 0 THEN
        RAISE EXCEPTION 'REFUSING: % has different sections from the master', v_var;
    END IF;

    SELECT count(*) INTO v_diff FROM (
        SELECT section_id, ord, html FROM resume_blocks WHERE doc_key = 'master' AND retired_at IS NULL
        EXCEPT SELECT section_id, ord, html FROM resume_blocks WHERE doc_key = v_bak AND retired_at IS NULL) d;
    IF v_diff <> 0 OR NOT EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_bak) THEN
        RAISE EXCEPTION 'REFUSING: backup % is missing or does not hold the current master (% rows differ)', v_bak, v_diff;
    END IF;

    DELETE FROM resume_blocks WHERE doc_key = 'master';
    INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html, retired_at, created_at)
    SELECT 'master', section_id, section_kind, ord, bullet_key, html, NULL, now()
      FROM resume_blocks WHERE doc_key = v_var AND retired_at IS NULL;
    GET DIAGNOSTICS v_n = ROW_COUNT;
    UPDATE resume_documents SET updated_at = now() WHERE doc_key = 'master';

    RAISE NOTICE 'OK - master now holds % blocks from %; the old master is kept as %', v_n, v_var, v_bak;
END $$;

COMMIT;
