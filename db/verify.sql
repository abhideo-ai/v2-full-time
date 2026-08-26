-- verify.sql — is the database in the state I think it is?
--
--   psql -d postgres -v ON_ERROR_STOP=1 -f db/verify.sql
--
-- One command, three databases, read-only. It prints what is there and RAISES on
-- anything that must not be. Run it after any migration, or months from now when
-- the only question is "did that ever actually land?".
--
-- It asserts INVARIANTS and prints FACTS, and the difference is deliberate:
--
--   invariant   something that must be true for as long as this repo exists —
--               jobs_tracker frozen at v1's 92 rows, v2 free of any archive
--               concept, neither database holding the other's seats. These raise.
--
--   fact        something true today that is SUPPOSED to change — how many v2
--               seats there are, what they scored. These print. An assertion on
--               a number `jobs_sync.py` refreshes would fail the first time the
--               tool did its job, and a check that cries wolf gets ignored.
--
-- Nothing here writes. Safe to run against anything, any time.

\pset pager off

-- ===========================================================================
-- jobs_tracker — v1's record. Frozen.
-- ===========================================================================
\c jobs_tracker
\echo ''
\echo '=== jobs_tracker (v1 — frozen, nothing in v2 reads or writes it) ==='

SELECT status, count(*) FROM applications GROUP BY 1 ORDER BY 2 DESC, 1;

SELECT (SELECT count(*) FROM applications)   AS applications,
       (SELECT count(*) FROM status_events)  AS status_events,
       (SELECT count(*) FROM scoring_events) AS scoring_events;

DO $$
DECLARE
  n_rows bigint;
  n_v2   bigint;
  n_col  bigint;
  n_chk  bigint;
  n_ev   bigint;
  got    text;
  -- v1's real distribution, recovered from `archived_from` by migration 006.
  -- These six numbers are the whole point of the column 003 added.
  want   text := 'applied=10, interviewing=1, new=15, recommended_skip=49, '
                 'resume_drafted=3, resume_finalized=14';
BEGIN
  SELECT count(*) INTO n_rows FROM applications;
  SELECT count(*) INTO n_v2   FROM applications
   WHERE scraped_at::date >= DATE '2026-08-25';
  SELECT count(*) INTO n_col  FROM information_schema.columns
   WHERE table_name = 'applications' AND column_name = 'archived_from';
  SELECT count(*) INTO n_chk  FROM pg_constraint
   WHERE conname = 'applications_archive_remembers';
  SELECT count(*) INTO n_ev   FROM status_events WHERE status = 'archived';
  SELECT string_agg(s || '=' || n, ', ' ORDER BY s) INTO got
    FROM (SELECT status::text AS s, count(*) AS n FROM applications GROUP BY 1) d;

  IF n_rows <> 92 THEN
    RAISE EXCEPTION 'jobs_tracker holds % row(s) — v1''s record is 92', n_rows;
  END IF;
  IF got <> want THEN
    RAISE EXCEPTION 'distribution is (%), v1''s record is (%)', got, want;
  END IF;
  IF n_v2 > 0 THEN
    RAISE EXCEPTION '% v2 seat(s) are in jobs_tracker — they belong in jobs_tracker_v2', n_v2;
  END IF;
  IF n_col > 0 OR n_chk > 0 OR n_ev > 0 THEN
    RAISE EXCEPTION 'archive residue survives: % column(s), % constraint(s), % event(s) '
                    '— migration 006 did not fully reverse 003', n_col, n_chk, n_ev;
  END IF;

  RAISE NOTICE 'OK — 92 v1 rows, original statuses, no archive residue';
  -- The one known, accepted difference from pre-003. PostgreSQL has no
  -- DROP VALUE, so 006 could not take it back out. Zero rows use it.
  IF EXISTS (SELECT 1 FROM unnest(enum_range(NULL::application_status)) v
              WHERE v::text = 'archived') THEN
    RAISE NOTICE 'note: the unused `archived` enum value remains — see 006, it cannot be dropped';
  END IF;
END $$;

-- ===========================================================================
-- jobs_tracker_v2 — v2's seats, and only v2's seats.
-- ===========================================================================
\c jobs_tracker_v2
\echo ''
\echo '=== jobs_tracker_v2 (v2 — what the launcher, jobs_sync and resume.py use) ==='

-- FACT, not an invariant: this list grows every time he pastes a JD, and the
-- scores are refreshed from each workspace's score.json by `jobs_sync.py`.
-- `at the move` is what migration 005 carried across on 2026-08-26, so drift
-- between the two columns is visible without being an error.
SELECT a.slug, a.status,
       a.fit_breakdown->>'technical' AS technical,
       m.moved                       AS "at the move"
  FROM applications a
  LEFT JOIN (VALUES ('yes-madam-lead-architect',           '88.375'),
                    ('principal-architect-ai-native',      '84.9'),
                    ('o9-senior-architect-agentic',        '81.4'),
                    ('wipro-principal-software-architect', '(no JD — unscored)'))
         AS m(slug, moved) ON m.slug = a.slug
 ORDER BY a.id;

SELECT (SELECT count(*) FROM applications)   AS applications,
       (SELECT count(*) FROM status_events)  AS status_events,
       (SELECT count(*) FROM scoring_events) AS scoring_events;

DO $$
DECLARE
  n_status bigint;
  n_arch   bigint;
  n_col    bigint;
  n_tables bigint;
  n_trig   bigint;
  n_v1     bigint;
  n_seats  bigint;
  missing  text;
BEGIN
  SELECT count(*) INTO n_status FROM unnest(enum_range(NULL::application_status));
  SELECT count(*) INTO n_arch   FROM unnest(enum_range(NULL::application_status)) v
   WHERE v::text = 'archived';
  SELECT count(*) INTO n_col    FROM information_schema.columns
   WHERE table_name = 'applications' AND column_name = 'archived_from';
  SELECT count(*) INTO n_tables FROM information_schema.tables
   WHERE table_schema = 'public'
     AND table_name IN ('applications', 'scoring_events', 'status_events');
  SELECT count(*) INTO n_trig   FROM pg_trigger
   WHERE tgname = 'applications_set_updated_at' AND NOT tgisinternal;
  SELECT count(*) INTO n_v1     FROM applications
   WHERE scraped_at::date < DATE '2026-08-25';
  SELECT count(*) INTO n_seats  FROM applications;

  -- The four migration 005 moved. Asserted by NAME, never by count: a fifth
  -- seat is expected, a missing one is not.
  SELECT string_agg(s, ', ') INTO missing
    FROM unnest(ARRAY['yes-madam-lead-architect', 'principal-architect-ai-native',
                      'o9-senior-architect-agentic',
                      'wipro-principal-software-architect']) AS s
   WHERE NOT EXISTS (SELECT 1 FROM applications a WHERE a.slug = s);

  IF n_tables <> 3 OR n_trig <> 1 THEN
    RAISE EXCEPTION 'schema incomplete: % of 3 table(s), % of 1 trigger — run migration 004',
      n_tables, n_trig;
  END IF;
  IF n_status <> 11 OR n_arch > 0 OR n_col > 0 THEN
    RAISE EXCEPTION 'the archive concept reached v2: % status value(s), % archived, % column(s). '
                    'v2 has no archive — see migration 004', n_status, n_arch, n_col;
  END IF;
  IF n_v1 > 0 THEN
    RAISE EXCEPTION '% row(s) predate 2026-08-25 — v1''s record belongs in jobs_tracker', n_v1;
  END IF;
  IF missing IS NOT NULL THEN
    RAISE EXCEPTION 'seat(s) missing from jobs_tracker_v2: % — migration 005 did not land', missing;
  END IF;

  RAISE NOTICE 'OK — % seat(s), all four originals present, 11 status values, no archive concept',
    n_seats;
END $$;

-- ===========================================================================
-- v2_daily — the daily log's task state. Untouched by any of this.
-- ===========================================================================
\c v2_daily
\echo ''
\echo '=== v2_daily (the daily log — untouched by the v1/v2 split) ==='

SELECT (SELECT count(*) FROM task_state) AS task_state,
       (SELECT count(*) FROM task_event) AS task_event;

DO $$
DECLARE
  n_tables bigint;
  n_reason bigint;
BEGIN
  SELECT count(*) INTO n_tables FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name IN ('task_state', 'task_event');
  -- Migration 001 turned the single `reason` into `reasons`; 002 closed the
  -- hole that let a move-out carry an empty one.
  SELECT count(*) INTO n_reason FROM information_schema.columns
   WHERE table_name = 'task_event' AND column_name = 'reasons';

  IF n_tables <> 2 THEN
    RAISE EXCEPTION 'v2_daily is missing a table — % of 2. Run db/schema.sql', n_tables;
  END IF;
  IF n_reason <> 1 THEN
    RAISE EXCEPTION 'task_event.reasons is missing — run migration 001';
  END IF;

  RAISE NOTICE 'OK — both tables present, migrations 001 and 002 applied';
END $$;

\echo ''
\echo 'All three databases verified.'
