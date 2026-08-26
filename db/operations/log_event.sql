-- db/operations/log_event.sql
--
-- Append one event to a seat's timeline. Meant to be run often - every InMail, every
-- reply, every document, every call.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
--        set_config('ev.slug','<slug>',false),
--        set_config('ev.kind','inbound|outbound|document|call|status|note',false),
--        set_config('ev.actor','<who>',false),
--        set_config('ev.summary','<one line>',false),
--        set_config('ev.detail','<verbatim text, optional>',false),
--        set_config('ev.artefact','<repo-relative path, optional>',false),
--        set_config('ev.at','<ISO timestamp, optional - defaults to now>',false)"
--        -f db/operations/log_event.sql
--
-- actor is REQUIRED. "someone sent a JD" is the shape of a record you cannot use later.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_slug text := current_setting('ev.slug', true);
    v_id   integer;
    v_at   timestamptz := COALESCE(
              nullif(trim(current_setting('ev.at', true)), '')::timestamptz, now());
BEGIN
    SELECT id INTO v_id FROM applications WHERE slug = v_slug;
    IF v_id IS NULL THEN RAISE EXCEPTION 'no application with slug %', v_slug; END IF;

    IF nullif(trim(current_setting('ev.actor', true)), '') IS NULL THEN
        RAISE EXCEPTION 'actor is required - who did this?';
    END IF;
    IF nullif(trim(current_setting('ev.summary', true)), '') IS NULL THEN
        RAISE EXCEPTION 'summary is required';
    END IF;

    INSERT INTO application_events
        (application_id, occurred_at, kind, actor, summary, detail, artefact)
    VALUES (v_id, v_at,
            current_setting('ev.kind', true)::event_kind,
            trim(current_setting('ev.actor', true)),
            trim(current_setting('ev.summary', true)),
            nullif(trim(current_setting('ev.detail', true)), ''),
            nullif(trim(current_setting('ev.artefact', true)), ''));

    RAISE NOTICE 'logged: % — %', v_slug, trim(current_setting('ev.summary', true));
END $$;

COMMIT;
