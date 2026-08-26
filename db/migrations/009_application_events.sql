-- 009_application_events.sql — jobs_tracker_v2
--
-- WHY: nothing recorded what actually HAPPENED on a seat.
--
-- status_events records that a row moved resume_drafted -> applied. It cannot record
-- that a recruiter sent an InMail on 26 August, that he replied the same day, that two
-- job descriptions came back four hours later, or that a CV was requested. Those are
-- the events a process is actually made of, and they are what v1 never had:
--
--   CLAUDE.md, "The v1 lesson on rooms" — one process ended in an unexplained
--   rejection with no recording, and another produced no debrief at all because the
--   recording failed. Neither cause is known. The record forbids guessing.
--
-- This table is that record. Append-only in spirit: correct by adding, not by editing.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/009_application_events.sql
--
-- Idempotent.

\set ON_ERROR_STOP on
BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_kind') THEN
        CREATE TYPE event_kind AS ENUM (
            'inbound',    -- they contacted him: InMail, email, call
            'outbound',   -- he contacted them: reply, application, follow-up
            'document',   -- something changed hands: a JD, a CV, a test
            'call',       -- a conversation happened or was scheduled
            'status',     -- the pipeline state moved
            'note'        -- an observation worth keeping that is none of the above
        );
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS application_events (
    id             serial PRIMARY KEY,
    application_id integer NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    occurred_at    timestamptz NOT NULL DEFAULT now(),
    kind           event_kind NOT NULL,
    -- Who did it. 'Abhisheik' for his own actions, a named human for theirs.
    -- Never left blank: "someone sent a JD" is the shape of a record you cannot use.
    actor          text NOT NULL,
    summary        text NOT NULL,          -- one line, scannable in a timeline
    detail         text,                   -- the message VERBATIM where one exists
    artefact       text,                   -- repo-relative path, when a file changed hands
    created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS application_events_app_time
    ON application_events (application_id, occurred_at);

COMMENT ON TABLE application_events IS
    'What actually happened on a seat, in order. status_events records the pipeline '
    'state; this records the correspondence, the documents and the calls behind it.';
COMMENT ON COLUMN application_events.detail IS
    'The message verbatim. A paraphrase six weeks later is not evidence of what was said.';

DO $$
BEGIN
    RAISE NOTICE 'OK — application_events ready';
END $$;

COMMIT;
