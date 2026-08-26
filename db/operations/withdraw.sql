-- db/operations/withdraw.sql
--
-- He steps away from a seat. Not a rejection - his call, with a reason.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
--        set_config('wd.slug','<slug>',false), set_config('wd.reason','<why>',false)" \
--        -f db/operations/withdraw.sql
--
-- A reason is REQUIRED. Same rule as ./todo: moving something out with no reason is
-- refused rather than invented, because the reason is what decides whether it can
-- ever come back. Writes the status change AND the timeline event, so the history
-- says why, not just that.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_slug   text := current_setting('wd.slug', true);
    v_reason text := nullif(trim(current_setting('wd.reason', true)), '');
    v_id     integer; v_prev text;
BEGIN
    SELECT id, status::text INTO v_id, v_prev FROM applications WHERE slug = v_slug;
    IF v_id IS NULL THEN RAISE EXCEPTION 'no application with slug %', v_slug; END IF;
    IF v_reason IS NULL THEN
        RAISE EXCEPTION 'a reason is required - why is % being withdrawn?', v_slug;
    END IF;
    IF v_prev = 'withdrawn' THEN
        RAISE NOTICE 'SKIP - % is already withdrawn', v_slug; RETURN;
    END IF;

    UPDATE applications SET status = 'withdrawn' WHERE id = v_id;
    INSERT INTO status_events (application_id, status, note, created_at)
    VALUES (v_id, 'withdrawn', format('withdrawn (was %s): %s', v_prev, v_reason), now());
    INSERT INTO application_events (application_id, kind, actor, summary, detail)
    VALUES (v_id, 'status', 'Abhisheik', format('Withdrawn: %s', v_reason),
            format('Previous status: %s', v_prev));

    RAISE NOTICE 'OK - % moved % -> withdrawn: %', v_slug, v_prev, v_reason;
END $$;

COMMIT;
