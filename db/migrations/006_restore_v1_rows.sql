-- 006 — give jobs_tracker back exactly what 003 changed, and nothing else.
--
--   psql -d jobs_tracker -f db/migrations/006_restore_v1_rows.sql
--
-- ⚠ Connect to `jobs_tracker`. Run 004 and 005 FIRST — this file deletes the
-- four v2 seats from here, and it refuses to delete any row it cannot find in
-- `jobs_tracker_v2`.
--
-- 003 archived v1's 92 rows in place. 004 and 005 gave v2 its own database, so
-- there is nothing left for the archive to do: `jobs_tracker` is v1's record and
-- only v1's record, and nothing in v2 reads or writes it. Non-interference means
-- leaving it the way v1 left it, not the way v2 found it convenient.
--
-- 003 promised "an exact reverse". This is that reverse, and it undoes all four
-- of the things 003 did:
--
--   1. status = archived_from on all 92 rows          (003 step 2, UPDATE)
--   2. drop the applications_archive_remembers CHECK  (003 step 2, constraint)
--   3. drop the applications.archived_from column     (003 step 2, column)
--   4. delete the 92 status_events rows it appended   (003 step 2, INSERT)
--
-- ⛔ IT CANNOT UNDO THE FIFTH: `ALTER TYPE application_status ADD VALUE
-- 'archived'`. PostgreSQL has no DROP VALUE and never has — removing it means
-- recreating the type, which means dropping and recreating every column and
-- index that depends on it, on the one database in this repo that must not be
-- rebuilt. So `archived` stays in the enum, unused, on zero rows. An enum value
-- nothing references is inert: it costs nothing, changes no plan, and cannot
-- appear in a query that does not ask for it. That is the correct trade, and it
-- is the ONE difference between this database and its pre-003 state.
--
-- (jobs_tracker_v2 never had it — 004's enum is eleven values, and its own
-- assertion refuses to commit if `archived` ever appears there.)
--
-- ⚠ `updated_at` IS PRESERVED AGAIN, for 003's reason: the BEFORE UPDATE
-- trigger would stamp all 92 rows with the moment of this migration and destroy
-- "when did v1 last touch this". 003 went to some trouble to keep those
-- timestamps; a reversal that overwrites them is not a reversal.
--
-- Idempotent: every step is guarded, so a second run restores nothing, deletes
-- nothing and still passes its own assertions.

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Delete the four v2 seats — but only the ones jobs_tracker_v2 confirms.
-- ---------------------------------------------------------------------------
-- This is the only DELETE in this repo's history against `jobs_tracker`, so it
-- carries a proof rather than a comment: each row is matched by id AND slug in
-- the other database before it goes. A seat that did not arrive there is a seat
-- that stays here. `scoring_events` and `status_events` cascade, and 005 has
-- already copied any that existed.
CREATE EXTENSION IF NOT EXISTS dblink;

CREATE TEMP TABLE _confirmed_in_v2 ON COMMIT DROP AS
  SELECT * FROM dblink('dbname=jobs_tracker_v2',
                       'SELECT id, slug FROM applications')
    AS v(id integer, slug text);

DELETE FROM applications a
 WHERE a.scraped_at::date >= DATE '2026-08-25'
   AND EXISTS (SELECT 1 FROM _confirmed_in_v2 v
                WHERE v.id = a.id AND v.slug = a.slug);

-- ---------------------------------------------------------------------------
-- 2. Un-archive the 92.
-- ---------------------------------------------------------------------------
-- 003's own documented reverse, verbatim: SET status = archived_from,
-- archived_from = NULL.
--
-- Guarded on the column still existing, and run through EXECUTE because of it:
-- step 4 drops `archived_from`, so on a second run this statement would not even
-- PARSE. A migration that cannot be run twice is a migration you are afraid of.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
              WHERE table_name = 'applications' AND column_name = 'archived_from') THEN
    EXECUTE 'ALTER TABLE applications DISABLE TRIGGER applications_set_updated_at';
    EXECUTE 'UPDATE applications SET status = archived_from, archived_from = NULL'
            ' WHERE status = ''archived'' AND archived_from IS NOT NULL';
    EXECUTE 'ALTER TABLE applications ENABLE TRIGGER applications_set_updated_at';
  ELSE
    RAISE NOTICE 'archived_from is already gone — nothing to un-archive';
  END IF;
END $$;

-- ---------------------------------------------------------------------------
-- 3. Delete the status_events 003 appended.
-- ---------------------------------------------------------------------------
-- Identified by exactly what 003 wrote: status 'archived' plus the note it
-- composed. Nothing else in this table can match — no other code path has ever
-- inserted an 'archived' event, and the 49 pre-existing rows predate 003 by
-- weeks. The note prefix is matched rather than the status alone so that a
-- hand-written archived event, if one ever existed, would survive.
DELETE FROM status_events
 WHERE status = 'archived'
   AND note LIKE 'Archived as part of v1''s record (scraped before 2026-08-25).%';

-- ---------------------------------------------------------------------------
-- 4. Drop the constraint and the column.
-- ---------------------------------------------------------------------------
-- Order matters: the CHECK reads the column, so it goes first.
ALTER TABLE applications DROP CONSTRAINT IF EXISTS applications_archive_remembers;
ALTER TABLE applications DROP COLUMN IF EXISTS archived_from;

DROP EXTENSION IF EXISTS dblink;

-- ---------------------------------------------------------------------------
-- 5. Prove it landed, or refuse to commit.
-- ---------------------------------------------------------------------------
-- The distribution below is 003's own recorded `archived_from` breakdown — the
-- thing that column existed to preserve — so this assertion is checking the
-- restore against v1's real record, not against a number someone remembered.
DO $$
DECLARE
  n_rows   bigint;
  n_arch   bigint;
  n_col    bigint;
  n_check  bigint;
  n_ev     bigint;
  n_v2     bigint;
  got      text;
  want     text := 'applied=10, interviewing=1, new=15, recommended_skip=49, '
                   'resume_drafted=3, resume_finalized=14';
BEGIN
  SELECT count(*) INTO n_rows FROM applications;
  SELECT count(*) INTO n_arch FROM applications WHERE status = 'archived';
  SELECT count(*) INTO n_col  FROM information_schema.columns
   WHERE table_name = 'applications' AND column_name = 'archived_from';
  SELECT count(*) INTO n_check FROM pg_constraint
   WHERE conname = 'applications_archive_remembers';
  SELECT count(*) INTO n_ev FROM status_events WHERE status = 'archived';
  SELECT count(*) INTO n_v2 FROM applications
   WHERE scraped_at::date >= DATE '2026-08-25';

  SELECT string_agg(s || '=' || n, ', ' ORDER BY s) INTO got
    FROM (SELECT status::text AS s, count(*) AS n
            FROM applications GROUP BY 1) d;

  IF n_arch > 0 THEN
    RAISE EXCEPTION '% row(s) are still archived', n_arch;
  END IF;
  IF n_col > 0 OR n_check > 0 THEN
    RAISE EXCEPTION 'archived_from (% col) / the CHECK (%) survived the drop', n_col, n_check;
  END IF;
  IF n_ev > 0 THEN
    RAISE EXCEPTION '% archived status_event(s) were not cleaned up', n_ev;
  END IF;
  IF n_v2 > 0 THEN
    RAISE EXCEPTION '% v2 seat(s) are still here — jobs_tracker_v2 did not confirm them, '
                    'so they were deliberately NOT deleted. Run 005 first', n_v2;
  END IF;
  IF n_rows <> 92 THEN
    RAISE EXCEPTION 'jobs_tracker holds % row(s), expected v1''s 92', n_rows;
  END IF;
  IF got <> want THEN
    RAISE EXCEPTION 'the recovered distribution is (%), expected (%)', got, want;
  END IF;

  RAISE NOTICE 'jobs_tracker restored — 92 v1 rows, distribution (%), no archive left', got;
END $$;

COMMIT;

-- Verify any time with:  psql -d postgres -f db/verify.sql
