-- 003 — archive v1's ninety-two rows, without losing what they were.
--
-- ⛔ HISTORY, NOT CURRENT STATE. This ran on 2026-08-26 and was REVERSED the
-- same day by `006_restore_v1_rows.sql`, once he asked for a separate database
-- instead: "let's use a different database? like jobs_tracker_v2? this way we DO
-- NOT interfere with v1 jobs?" `jobs_tracker` has no archived rows and no
-- `archived_from` column today, and that is correct — do not re-run this file.
-- It is kept because 006 is only readable next to it, and because the
-- `archived_from` column it invented is what let the reversal recover v1's exact
-- status distribution. Read 004, 005 and 006 for where things actually stand.
--
--   psql -d jobs_tracker -f db/migrations/003_archive_v1_rows.sql
--
-- ⚠ This is the FIRST migration against `jobs_tracker`. 001 and 002 are
-- `v2_daily`'s. Read the connection string above before running it.
--
-- v1's record is 92 rows scraped before 2026-08-25; the four live v2 seats were
-- all created on 2026-08-25. He asked for the old ones out of the way, filtered
-- on the status column, so `archived` joins `application_status` and the launcher
-- gives it a tab of its own that `all` excludes.
--
-- ARCHIVING IS A STATUS CHANGE AND NOTHING ELSE. No row is deleted. The 49
-- `recommended_skip` decisions, the 10 sends, the 14 finalised-and-unsent are the
-- evidence behind every response-rate and backlog figure CLAUDE.md quotes, so
-- what each row WAS has to survive being archived:
--
--   applications.archived_from  — the authoritative previous status. One column,
--       one query (`SELECT archived_from, count(*) … GROUP BY 1`), and an exact
--       reverse (`SET status = archived_from, archived_from = NULL`). A CHECK
--       constraint makes it mandatory, in the same spirit as 001's
--       "a move-out must carry a reason": the database refuses an archive that
--       forgets where the row came from, rather than trusting every caller.
--
--   status_events              — one appended row per archive, for WHEN. It is
--       this schema's existing append-only history and it carries the timestamp
--       the column cannot.
--
-- Both, because neither does the other's job: the column is queryable and
-- reversible, the event is dated. Only 49 of the 96 rows have any status_events
-- history at all, so the event log alone could not be trusted to answer
-- "what was this before?".
--
-- ⚠ `updated_at` IS DELIBERATELY PRESERVED. The BEFORE UPDATE trigger would
-- stamp all 92 rows with the moment of the migration, which destroys "when did
-- v1 last touch this" and collapses the archived tab into one timestamp. The
-- trigger is disabled for the one statement and re-enabled immediately; the
-- archive's own timestamp lives in `status_events.created_at`.
--
-- Idempotent: every statement is guarded on `status <> 'archived'`, so a second
-- run archives nothing and appends no event.

-- ---------------------------------------------------------------------------
-- 1. The enum value, on its own.
-- ---------------------------------------------------------------------------
-- PostgreSQL 12+ allows ADD VALUE inside a transaction block but forbids USING
-- the new value until that transaction commits — and the CHECK constraint below
-- uses it. So this one runs and commits by itself.
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'archived';

-- ---------------------------------------------------------------------------
-- 2. The column, the constraint, the archive.
-- ---------------------------------------------------------------------------
BEGIN;

ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS archived_from application_status;

COMMENT ON COLUMN applications.archived_from IS
  'The status this row held before it was archived. NULL unless status = ''archived''. '
  'Restore with: UPDATE applications SET status = archived_from, archived_from = NULL.';

-- The invariant in both directions: archived rows remember, live rows do not
-- carry a stale memory, and nothing is ever "archived from archived".
ALTER TABLE applications DROP CONSTRAINT IF EXISTS applications_archive_remembers;
ALTER TABLE applications ADD  CONSTRAINT applications_archive_remembers
  CHECK (
    CASE WHEN status = 'archived'
         THEN archived_from IS NOT NULL AND archived_from <> 'archived'
         ELSE archived_from IS NULL
    END
  );

-- Row count before, so the assertion at the end compares against a fact rather
-- than a number typed into this file.
CREATE TEMP TABLE _archive_before ON COMMIT DROP AS
  SELECT count(*) AS total,
         count(*) FILTER (WHERE status <> 'archived'
                            AND scraped_at::date < DATE '2026-08-25') AS to_archive
    FROM applications;

-- History first: it reads the status that is about to change.
INSERT INTO status_events (application_id, status, note)
SELECT id,
       'archived'::application_status,
       'Archived as part of v1''s record (scraped before 2026-08-25). Previous status '
         || status::text || ' is kept in applications.archived_from; updated_at was '
         'deliberately left at ' || updated_at::text || '.'
  FROM applications
 WHERE status <> 'archived'
   AND scraped_at::date < DATE '2026-08-25';

ALTER TABLE applications DISABLE TRIGGER applications_set_updated_at;

UPDATE applications
   SET archived_from = status,
       status = 'archived'
 WHERE status <> 'archived'
   AND scraped_at::date < DATE '2026-08-25';

ALTER TABLE applications ENABLE TRIGGER applications_set_updated_at;

-- ---------------------------------------------------------------------------
-- 3. Prove it, or refuse to commit.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  before_total  bigint;
  before_target bigint;
  after_total   bigint;
  n_archived    bigint;
  n_forgot      bigint;
  n_left        bigint;
BEGIN
  SELECT total, to_archive INTO before_total, before_target FROM _archive_before;
  SELECT count(*) INTO after_total FROM applications;
  SELECT count(*) INTO n_archived  FROM applications WHERE status = 'archived';
  SELECT count(*) INTO n_forgot    FROM applications
   WHERE status = 'archived' AND archived_from IS NULL;
  SELECT count(*) INTO n_left      FROM applications
   WHERE status <> 'archived' AND scraped_at::date < DATE '2026-08-25';

  IF after_total <> before_total THEN
    RAISE EXCEPTION 'row count changed: % before, % after — archiving must never delete',
      before_total, after_total;
  END IF;
  IF n_forgot > 0 THEN
    RAISE EXCEPTION '% archived row(s) lost their previous status', n_forgot;
  END IF;
  IF n_left > 0 THEN
    RAISE EXCEPTION '% row(s) older than 2026-08-25 were not archived', n_left;
  END IF;

  RAISE NOTICE 'archived % row(s) this run; % archived in total; % row(s) untouched',
    before_target, n_archived, after_total - n_archived;
END $$;

COMMIT;

-- Read it back:
--   SELECT archived_from, count(*) FROM applications
--    WHERE status = 'archived' GROUP BY 1 ORDER BY 2 DESC;
