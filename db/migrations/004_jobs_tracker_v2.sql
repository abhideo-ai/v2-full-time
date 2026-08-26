-- 004 — jobs_tracker_v2: v2 gets its own database, so v1's is never touched.
--
--   psql -d postgres -f db/migrations/004_jobs_tracker_v2.sql
--
-- ⚠ Connect to `postgres`, not to `jobs_tracker`. This file creates a database
-- and then \c's into it. 001 and 002 are `v2_daily`'s; 003 and 006 are
-- `jobs_tracker`'s; 004 and 005 are this one's.
--
-- WHY A SECOND DATABASE AND NOT A STATUS FLAG
--
-- 003 archived v1's 92 rows in place, behind `status = 'archived'` and a tab of
-- their own. It worked, but it left every reader of this schema carrying v1: the
-- launcher needed an archived tab, `jobs_db.py` needed an `archived_from`
-- column in its SELECT and a rule for what an archived row's "reached" status
-- was, and every count had to be qualified with "…excluding archived". A row
-- that must be filtered out of every view is a row in the wrong database.
--
-- His words: "let's use a different database? like jobs_tracker_v2? this way we
-- DO NOT interfere with v1 jobs?" — so:
--
--   jobs_tracker      v1's 92 rows, restored by 006 to exactly the statuses they
--                     held before 003. Nothing in v2 reads or writes it.
--   jobs_tracker_v2   v2's seats, and only ever v2's seats. What the launcher,
--                     `jobs_sync.py` and `resume.py new` talk to.
--
-- Non-interference is the whole point, and it is now enforced by the connection
-- string rather than by every query remembering to exclude a status.
--
-- THE SCHEMA IS DERIVED, NOT RETYPED. Everything below is `pg_dump --schema-only
-- -d jobs_tracker`, so it cannot drift from what `jobs_db.py` selects, with
-- EXACTLY THREE OMISSIONS — the three things 003 added and 006 takes back out:
--
--   1. the `archived` value on `application_status`
--   2. the `applications.archived_from` column and its COMMENT
--   3. the `applications_archive_remembers` CHECK constraint
--
-- Omitting them is deliberate and is the other half of removing the archived
-- concept from v2's code path. `jobs_db.tab_for()` raises on a status it has no
-- tab for; with `archived` absent from the enum as well, the database refuses
-- the row before the Python ever sees it. Two independent refusals, no residue.
--
-- Idempotent: safe to re-run. It creates nothing that already exists and drops
-- nothing at all.

-- ---------------------------------------------------------------------------
-- 1. The database.
-- ---------------------------------------------------------------------------
-- PostgreSQL has no CREATE DATABASE IF NOT EXISTS, and CREATE DATABASE cannot
-- run inside a transaction block. \gexec runs the SELECT's result as SQL, which
-- is nothing at all on a re-run.
SELECT 'CREATE DATABASE jobs_tracker_v2'
 WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'jobs_tracker_v2')
\gexec

\c jobs_tracker_v2

BEGIN;

-- ---------------------------------------------------------------------------
-- 2. The enums.
-- ---------------------------------------------------------------------------
-- There is no CREATE TYPE IF NOT EXISTS either. Swallowing duplicate_object is
-- the documented way to make an enum idempotent.
--
-- ⚠ `application_status` is ELEVEN values here, not twelve. `archived` is
-- absent on purpose — see the header. `jobs_db.TAB_FOR_STATUS` maps exactly
-- these eleven, and `automation/tests/test_jobs_db.py` asserts the two sets are
-- equal, so adding a value here without adding a tab fails the suite.
DO $$ BEGIN
  CREATE TYPE application_status AS ENUM (
      'new',
      'recommended_apply',
      'recommended_skip',
      'resume_drafted',
      'resume_finalized',
      'applied',
      'heard_back',
      'interviewing',
      'offer',
      'rejected',
      'withdrawn'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE application_type AS ENUM ('full_time', 'freelancing');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE freelancing_track AS ENUM ('tailor', 'spray');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- 3. The updated_at trigger function.
-- ---------------------------------------------------------------------------
-- ⚠ plpgsql. 003's sibling note applies: if a PostgreSQL install loses
-- `$libdir/plpgsql.so` every UPDATE on `applications` fails with UndefinedFile.
-- `jobs_sync._update_score` carries the retry for that case.
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

-- ---------------------------------------------------------------------------
-- 4. The tables.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
    id                  serial,
    slug                text NOT NULL,
    type                application_type NOT NULL,
    company             text NOT NULL,
    role                text NOT NULL,
    source_url          text NOT NULL,
    location            text,
    -- ⛔ Never selected and never rendered. Compensation is deferred by user
    -- directive; the column exists only because the schema is derived verbatim.
    -- `test_jobs_db.py` asserts "salary" appears nowhere in `jobs_db._SELECT`.
    salary              text,
    jd_text             text,
    jd_html             text,
    recommendation      text,
    rec_reasoning       text,
    status              application_status DEFAULT 'new'::application_status NOT NULL,
    scraped_at          timestamp with time zone DEFAULT now() NOT NULL,
    applied_at          timestamp with time zone,
    updated_at          timestamp with time zone DEFAULT now() NOT NULL,
    posted_at           timestamp with time zone,
    posted_at_text      text,
    fit_score           integer,
    fit_breakdown       jsonb,
    hiring_contacts     jsonb,
    ats_resume_score    integer,
    submitted_to_upgrad timestamp with time zone,
    track               freelancing_track,
    CONSTRAINT applications_pkey PRIMARY KEY (id),
    CONSTRAINT applications_slug_key UNIQUE (slug)
);

CREATE TABLE IF NOT EXISTS scoring_events (
    id             serial,
    application_id integer NOT NULL,
    fit_score      integer NOT NULL,
    fit_breakdown  jsonb NOT NULL,
    recommendation text,
    rec_reasoning  text,
    source         text DEFAULT 'manual'::text NOT NULL,
    claude_model   text,
    prompt_version text,
    note           text,
    scored_at      timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT scoring_events_pkey PRIMARY KEY (id),
    CONSTRAINT scoring_events_application_id_fkey
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- Append-only history: one row per status change, with the timestamp the
-- `applications` row itself cannot carry.
CREATE TABLE IF NOT EXISTS status_events (
    id             serial,
    application_id integer NOT NULL,
    status         application_status NOT NULL,
    note           text,
    created_at     timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT status_events_pkey PRIMARY KEY (id),
    CONSTRAINT status_events_application_id_fkey
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------------
-- 5. Indexes and the trigger.
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS applications_fit_score_idx
    ON applications USING btree (fit_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS applications_posted_at_idx
    ON applications USING btree (posted_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS applications_status_idx
    ON applications USING btree (status);
CREATE INDEX IF NOT EXISTS applications_type_status_idx
    ON applications USING btree (type, status);
CREATE INDEX IF NOT EXISTS applications_type_track_idx
    ON applications USING btree (type, track)
    WHERE (type = 'freelancing'::application_type);
CREATE INDEX IF NOT EXISTS scoring_events_application_id_idx
    ON scoring_events USING btree (application_id, scored_at DESC);
CREATE INDEX IF NOT EXISTS scoring_events_scored_at_idx
    ON scoring_events USING btree (scored_at DESC);

CREATE OR REPLACE TRIGGER applications_set_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- 6. Prove the shape, or refuse to commit.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  n_status  bigint;
  n_arch    bigint;
  n_col     bigint;
  n_tables  bigint;
  n_trigger bigint;
BEGIN
  SELECT count(*) INTO n_status FROM unnest(enum_range(NULL::application_status));
  SELECT count(*) INTO n_arch   FROM unnest(enum_range(NULL::application_status)) v
   WHERE v::text = 'archived';
  SELECT count(*) INTO n_col FROM information_schema.columns
   WHERE table_name = 'applications' AND column_name = 'archived_from';
  SELECT count(*) INTO n_tables FROM information_schema.tables
   WHERE table_schema = 'public'
     AND table_name IN ('applications', 'scoring_events', 'status_events');
  SELECT count(*) INTO n_trigger FROM pg_trigger
   WHERE tgname = 'applications_set_updated_at' AND NOT tgisinternal;

  IF n_tables <> 3 THEN
    RAISE EXCEPTION 'expected 3 tables, found %', n_tables;
  END IF;
  IF n_status <> 11 THEN
    RAISE EXCEPTION 'application_status should hold 11 values in v2, found %', n_status;
  END IF;
  IF n_arch > 0 THEN
    RAISE EXCEPTION 'the archived enum value reached jobs_tracker_v2 — v2 has no archive';
  END IF;
  IF n_col > 0 THEN
    RAISE EXCEPTION 'applications.archived_from reached jobs_tracker_v2 — v2 has no archive';
  END IF;
  IF n_trigger <> 1 THEN
    RAISE EXCEPTION 'the updated_at trigger is missing';
  END IF;

  RAISE NOTICE 'jobs_tracker_v2 ready — 3 tables, % status values, no archive residue', n_status;
END $$;

COMMIT;

-- Next: 005 moves the four v2 seats in, 006 gives jobs_tracker its 92 rows back.
