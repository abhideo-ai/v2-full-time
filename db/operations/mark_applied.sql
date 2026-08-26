-- db/operations/mark_applied.sql
--
-- Mark one seat as SENT. This is an OPERATION, not a migration: it is meant to be
-- re-run, once per application, for the rest of the search.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 \
--        -v slug="'yes-madam-lead-architect'" -f db/operations/mark_applied.sql
--
-- Why a file and not a one-liner: every schema or data change in this repo lives in
-- db/ as .sql so it is re-runnable and verifiable later. A status change is a data
-- change. It also writes the status_events row by hand, which a bare UPDATE would
-- forget -- and that history is how "when did this go out" survives.
--
-- Idempotent: re-running on an already-applied seat changes nothing and says so.

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    v_slug  text := current_setting('mark_applied.slug', true);
    v_id    integer;
    v_prev  text;
BEGIN
    SELECT id, status::text INTO v_id, v_prev
      FROM applications WHERE slug = v_slug;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'no application with slug %', v_slug;
    END IF;

    IF v_prev = 'applied' THEN
        RAISE NOTICE 'SKIP - % is already applied, nothing to do', v_slug;
        RETURN;
    END IF;

    UPDATE applications
       SET status     = 'applied',
           applied_at = COALESCE(applied_at, now())
     WHERE id = v_id;

    INSERT INTO status_events (application_id, status, note, created_at)
    VALUES (v_id, 'applied', format('sent (was %s)', v_prev), now());

    RAISE NOTICE 'OK - % moved % -> applied', v_slug, v_prev;
END $$;

COMMIT;
