-- db/operations/set_status.sql
--
-- Move one seat to a new status - interviewing, heard_back, offer, rejected, and the
-- rest. This is an OPERATION, not a migration: it is meant to be re-run, once per
-- status change, for the rest of the search.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('set_status.slug','<slug>',false), set_config('set_status.status','<status>',false), set_config('set_status.note','<reason>',false)" -f db/operations/set_status.sql
--
-- A note is REQUIRED. A status change must carry its reason; it lands in the
-- status_events row as "<note> (was <previous status>)", so the history says why,
-- not just that. A bare UPDATE would write the status and forget the history.
--
-- Two targets are refused because each has its own operation that writes more than
-- the status: applied -> mark_applied.sql (also sets applied_at), withdrawn ->
-- withdraw.sql (also writes the timeline event).
--
-- Idempotent: re-running on a seat already at that status changes nothing and says so.
-- updated_at is left to the applications_set_updated_at trigger.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_slug text := current_setting('set_status.slug', true);
    v_new  text := current_setting('set_status.status', true);
    v_note text := nullif(trim(current_setting('set_status.note', true)), '');
    v_id   integer; v_prev text;
BEGIN
    SELECT id, status::text INTO v_id, v_prev FROM applications WHERE slug = v_slug;
    IF v_id IS NULL THEN RAISE EXCEPTION 'no application with slug %', v_slug; END IF;

    IF v_new IS NULL OR NOT v_new = ANY (enum_range(NULL::application_status)::text[]) THEN
        RAISE EXCEPTION 'status % is not an application_status - one of: %',
            quote_nullable(v_new), array_to_string(enum_range(NULL::application_status), ', ');
    END IF;
    IF v_new = 'applied' THEN
        RAISE EXCEPTION 'applied is not set here - use db/operations/mark_applied.sql, which also sets applied_at';
    END IF;
    IF v_new = 'withdrawn' THEN
        RAISE EXCEPTION 'withdrawn is not set here - use db/operations/withdraw.sql, which also writes the timeline event';
    END IF;

    IF v_note IS NULL THEN
        RAISE EXCEPTION 'a note is required - why is % moving to %?', v_slug, v_new;
    END IF;
    IF v_prev = v_new THEN
        RAISE NOTICE 'SKIP - % is already %, nothing to do', v_slug, v_new; RETURN;
    END IF;

    UPDATE applications SET status = v_new::application_status WHERE id = v_id;
    INSERT INTO status_events (application_id, status, note, created_at)
    VALUES (v_id, v_new::application_status, format('%s (was %s)', v_note, v_prev), now());

    RAISE NOTICE 'OK - % moved % -> %', v_slug, v_prev, v_new;
END $$;

COMMIT;
