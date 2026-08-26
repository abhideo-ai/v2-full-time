-- 007_source_url_nullable.sql — jobs_tracker_v2
--
-- WHY: applications.source_url was NOT NULL, so a seat with no posting URL had
-- nowhere honest to put that fact. Every such row was filled with prose instead:
--
--   "naukri (listing URL not captured)"
--   "linkedin-inmail (inbound recruiter outreach — no URL supplied)"
--
-- The launcher reads that column as an href, so prose rendered as a broken link
-- that looked real. A URL column should hold a URL or nothing.
--
-- Some seats genuinely have no URL and never will: an inbound recruiter InMail has
-- no public posting. NULL is the correct representation of that, and the launcher
-- already handles it — static/apps.js falls through to "no workspace, no posting URL".
--
-- Applies to jobs_tracker_v2 ONLY. jobs_tracker is v1's frozen record; nothing in v2
-- opens it.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/007_source_url_nullable.sql
--
-- Idempotent: re-running is a no-op.

\set ON_ERROR_STOP on
BEGIN;

ALTER TABLE applications ALTER COLUMN source_url DROP NOT NULL;

-- Clear every value that is not actually a URL. Prose here is the bug.
UPDATE applications
   SET source_url = NULL
 WHERE source_url IS NOT NULL
   AND source_url !~ '^https?://';

DO $$
DECLARE
    v_prose integer;
    v_null  boolean;
BEGIN
    SELECT count(*) INTO v_prose
      FROM applications
     WHERE source_url IS NOT NULL AND source_url !~ '^https?://';

    SELECT is_nullable = 'YES' INTO v_null
      FROM information_schema.columns
     WHERE table_name = 'applications' AND column_name = 'source_url';

    IF v_prose > 0 THEN
        RAISE EXCEPTION 'still % non-URL value(s) in source_url', v_prose;
    END IF;
    IF NOT v_null THEN
        RAISE EXCEPTION 'source_url is still NOT NULL';
    END IF;

    RAISE NOTICE 'OK - source_url is nullable and holds only URLs or NULL';
END $$;

COMMIT;
