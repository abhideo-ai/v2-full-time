-- 005 — move v2's seats out of jobs_tracker and into jobs_tracker_v2.
--
--   psql -d jobs_tracker_v2 -f db/migrations/005_move_v2_seats.sql
--
-- ⚠ Connect to `jobs_tracker_v2`. Run 004 first; run 006 after. Order matters:
-- 006 deletes these rows from `jobs_tracker`, and it refuses to delete a row it
-- cannot find here.
--
-- COPIED, NOT RETYPED. The four seats are read across the connection with
-- dblink and inserted column for column. Nothing about them is typed into this
-- file — not a slug, not a company, not a score. A migration that restates
-- 88.375 by hand is a migration that can be wrong about 88.375.
--
-- WHICH ROWS: `scraped_at::date >= DATE '2026-08-25'`. The same line 003 drew,
-- from the other side. v1's record is everything taken in before that date; v2
-- began on it. There is no second criterion and no list of slugs, so a fifth
-- seat registered before this ran would come across too.
--
-- WHAT COMES WITH THEM: `scoring_events` and `status_events`, by foreign key.
-- Both happen to be empty for these four right now — nothing re-scored through
-- `scoring_events`, no status moved through `status_events` — but a migration
-- that only handles the rows it happened to see is a migration that loses the
-- first row it did not.
--
-- IDS ARE PRESERVED. The four keep 99-102 rather than being renumbered to 1-4,
-- so their event foreign keys need no remapping and a row can still be matched
-- across the two databases by id while both copies exist. The sequences are
-- advanced afterwards; an explicit-id INSERT does not move them, and the next
-- `resume.py new` would otherwise collide on the primary key.
--
-- ⛔ `salary` IS DELIBERATELY NOT COPIED. Compensation is deferred, all four
-- rows carry NULL, and the column list below is the one place a future reader
-- would look to see that it was a decision rather than an oversight.
--
-- Idempotent: ON CONFLICT DO NOTHING on every insert, so a re-run moves nothing
-- and changes nothing.

BEGIN;

CREATE EXTENSION IF NOT EXISTS dblink;

-- ---------------------------------------------------------------------------
-- 1. The seats.
-- ---------------------------------------------------------------------------
INSERT INTO applications (
    id, slug, type, company, role, source_url, location,
    jd_text, jd_html, recommendation, rec_reasoning, status,
    scraped_at, applied_at, updated_at, posted_at, posted_at_text,
    fit_score, fit_breakdown, hiring_contacts, ats_resume_score,
    submitted_to_upgrad, track)
SELECT id, slug, type::application_type, company, role, source_url, location,
       jd_text, jd_html, recommendation, rec_reasoning, status::application_status,
       scraped_at, applied_at, updated_at, posted_at, posted_at_text,
       fit_score, fit_breakdown, hiring_contacts, ats_resume_score,
       submitted_to_upgrad, track::freelancing_track
  FROM dblink('dbname=jobs_tracker', $q$
        SELECT id, slug, type::text, company, role, source_url, location,
               jd_text, jd_html, recommendation, rec_reasoning, status::text,
               scraped_at, applied_at, updated_at, posted_at, posted_at_text,
               fit_score, fit_breakdown, hiring_contacts, ats_resume_score,
               submitted_to_upgrad, track::text
          FROM applications
         WHERE scraped_at::date >= DATE '2026-08-25'
         ORDER BY id
       $q$) AS src(
        id integer, slug text, type text, company text, role text,
        source_url text, location text, jd_text text, jd_html text,
        recommendation text, rec_reasoning text, status text,
        scraped_at timestamptz, applied_at timestamptz, updated_at timestamptz,
        posted_at timestamptz, posted_at_text text, fit_score integer,
        fit_breakdown jsonb, hiring_contacts jsonb, ats_resume_score integer,
        submitted_to_upgrad timestamptz, track text)
ON CONFLICT (id) DO NOTHING;

-- The enums cross as text and are cast back on the way in. That is not laziness:
-- `application_status` has twelve values over there and eleven here, so a binary
-- transfer of the type is not even possible — and an `archived` row arriving in
-- v2 would fail the cast rather than land silently. The type mismatch IS the
-- guard.
--
-- ⚠ `updated_at` survives because the BEFORE UPDATE trigger is UPDATE-only and
-- these are INSERTs. Nothing is disabled, unlike 003.

-- ---------------------------------------------------------------------------
-- 2. Their history.
-- ---------------------------------------------------------------------------
INSERT INTO scoring_events (
    id, application_id, fit_score, fit_breakdown, recommendation,
    rec_reasoning, source, claude_model, prompt_version, note, scored_at)
SELECT id, application_id, fit_score, fit_breakdown, recommendation,
       rec_reasoning, source, claude_model, prompt_version, note, scored_at
  FROM dblink('dbname=jobs_tracker', $q$
        SELECT se.id, se.application_id, se.fit_score, se.fit_breakdown,
               se.recommendation, se.rec_reasoning, se.source, se.claude_model,
               se.prompt_version, se.note, se.scored_at
          FROM scoring_events se
          JOIN applications a ON a.id = se.application_id
         WHERE a.scraped_at::date >= DATE '2026-08-25'
       $q$) AS src(
        id integer, application_id integer, fit_score integer,
        fit_breakdown jsonb, recommendation text, rec_reasoning text,
        source text, claude_model text, prompt_version text, note text,
        scored_at timestamptz)
ON CONFLICT (id) DO NOTHING;

INSERT INTO status_events (id, application_id, status, note, created_at)
SELECT id, application_id, status::application_status, note, created_at
  FROM dblink('dbname=jobs_tracker', $q$
        SELECT ev.id, ev.application_id, ev.status::text, ev.note, ev.created_at
          FROM status_events ev
          JOIN applications a ON a.id = ev.application_id
         WHERE a.scraped_at::date >= DATE '2026-08-25'
       $q$) AS src(
        id integer, application_id integer, status text, note text,
        created_at timestamptz)
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. Advance the sequences past the ids we forced in.
-- ---------------------------------------------------------------------------
-- setval to max(id), or back to 1 when a table is empty. Without this the next
-- INSERT would hand out id 1 and collide with the row that already holds 99.
SELECT setval(pg_get_serial_sequence('applications',   'id'),
              coalesce(max(id), 1), max(id) IS NOT NULL) FROM applications;
SELECT setval(pg_get_serial_sequence('scoring_events', 'id'),
              coalesce(max(id), 1), max(id) IS NOT NULL) FROM scoring_events;
SELECT setval(pg_get_serial_sequence('status_events',  'id'),
              coalesce(max(id), 1), max(id) IS NOT NULL) FROM status_events;

-- ---------------------------------------------------------------------------
-- 4. Prove every seat arrived intact, or refuse to commit.
-- ---------------------------------------------------------------------------
-- The comparison is row-by-row against the source, not against numbers typed
-- here: every column that has to survive the move is checked back across the
-- connection. 006 deletes the originals, so this is the last moment a
-- discrepancy can be caught while both copies still exist.
DO $$
DECLARE
  n_src   bigint;
  n_here  bigint;
  n_match bigint;
  n_ev    bigint;
  n_extra bigint;
BEGIN
  CREATE TEMP TABLE _src ON COMMIT DROP AS
    SELECT * FROM dblink('dbname=jobs_tracker', $q$
        SELECT id, slug, company, role, status::text, location, source_url,
               fit_score, fit_breakdown, scraped_at, applied_at, updated_at
          FROM applications
         WHERE scraped_at::date >= DATE '2026-08-25'
      $q$) AS s(
        id integer, slug text, company text, role text, status text,
        location text, source_url text, fit_score integer, fit_breakdown jsonb,
        scraped_at timestamptz, applied_at timestamptz, updated_at timestamptz);

  SELECT count(*) INTO n_src  FROM _src;
  SELECT count(*) INTO n_here FROM applications;

  -- IS NOT DISTINCT FROM, so a NULL on both sides counts as equal: Wipro has no
  -- score and no location, and it must still match.
  SELECT count(*) INTO n_match
    FROM applications a JOIN _src s ON s.id = a.id
   WHERE a.slug          IS NOT DISTINCT FROM s.slug
     AND a.company       IS NOT DISTINCT FROM s.company
     AND a.role          IS NOT DISTINCT FROM s.role
     AND a.status::text  IS NOT DISTINCT FROM s.status
     AND a.location      IS NOT DISTINCT FROM s.location
     AND a.source_url    IS NOT DISTINCT FROM s.source_url
     AND a.fit_score     IS NOT DISTINCT FROM s.fit_score
     AND a.fit_breakdown IS NOT DISTINCT FROM s.fit_breakdown
     AND a.scraped_at    IS NOT DISTINCT FROM s.scraped_at
     AND a.applied_at    IS NOT DISTINCT FROM s.applied_at
     AND a.updated_at    IS NOT DISTINCT FROM s.updated_at;

  SELECT count(*) INTO n_extra FROM applications a
   WHERE NOT EXISTS (SELECT 1 FROM _src s WHERE s.id = a.id);

  SELECT (SELECT count(*) FROM scoring_events) + (SELECT count(*) FROM status_events)
    INTO n_ev;

  IF n_src = 0 THEN
    RAISE EXCEPTION 'jobs_tracker holds no seat scraped on or after 2026-08-25 — '
                    'either 006 already ran, or the wrong database was named';
  END IF;
  IF n_match <> n_src THEN
    RAISE EXCEPTION 'only % of % seat(s) came across with every field intact',
      n_match, n_src;
  END IF;
  IF n_here <> n_src + n_extra THEN
    RAISE EXCEPTION 'jobs_tracker_v2 holds % row(s), expected % + % pre-existing',
      n_here, n_src, n_extra;
  END IF;

  RAISE NOTICE 'moved % seat(s) with every field intact; % event row(s) with them; '
               '% row(s) already here', n_src, n_ev, n_extra;
END $$;

COMMIT;

-- Read it back:
--   SELECT slug, status, fit_breakdown->>'technical' AS technical
--     FROM applications ORDER BY id;
--
-- Expected: yes-madam-lead-architect 88.375 · principal-architect-ai-native 84.9
--           o9-senior-architect-agentic 81.4 · wipro-principal-software-architect
--           NULL (no job description, so nothing to score).
--
-- dblink stays installed: 006 reads back across it to confirm these arrived
-- before it deletes the originals. Drop it afterwards if you want the extension
-- list clean — nothing in the Python uses it.
