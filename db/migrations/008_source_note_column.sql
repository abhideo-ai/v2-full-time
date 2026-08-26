-- 008_source_note_column.sql — jobs_tracker_v2
--
-- WHY: source_url was doing two jobs. jobs_db.py split it by prefix — a value
-- starting with http became the link, anything else became a "note" — which kept
-- prose out of the href but made the two facts mutually exclusive. They are not.
--
-- o9 is the case that proves it: he APPLIED through naukri.com, and the requisition
-- the description was traced to lives on o9's own Workday site. That is a URL and a
-- note, and the old shape could hold only one.
--
-- 007 made source_url nullable and cleared the prose, which was right for the column
-- but dropped the reasons with it. This gives them a home.
--
-- After this: source_url is a URL or NULL, never prose. source_note is free text or
-- NULL. A row may carry either, both, or — only while a seat is mid-intake — neither.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/008_source_note_column.sql
--
-- Idempotent.

\set ON_ERROR_STOP on
BEGIN;

ALTER TABLE applications ADD COLUMN IF NOT EXISTS source_note text;

-- Any prose still sitting in source_url moves across rather than being deleted.
UPDATE applications
   SET source_note = COALESCE(source_note, source_url),
       source_url  = NULL
 WHERE source_url IS NOT NULL
   AND source_url !~ '^https?://';

-- Restore the notes 007 cleared, from what each workspace's jd.md actually records.
UPDATE applications SET source_note = 'Naukri listing — URL not captured at intake'
 WHERE slug IN ('yes-madam-lead-architect', 'principal-architect-ai-native')
   AND source_note IS NULL;

UPDATE applications SET source_note = 'Inbound recruiter InMail — no public posting exists'
 WHERE slug IN ('wipro-principal-software-architect',
                'wolters-kluwer-principal-ai-platform-engineer')
   AND source_note IS NULL;

UPDATE applications SET source_note = 'Applied through naukri.com; the URL is the o9 requisition '
                                      'JR102297 the description was traced to'
 WHERE slug = 'o9-senior-architect-agentic' AND source_note IS NULL;

DO $$
DECLARE v_bad integer; v_orphan integer;
BEGIN
    SELECT count(*) INTO v_bad FROM applications
     WHERE source_url IS NOT NULL AND source_url !~ '^https?://';
    IF v_bad > 0 THEN RAISE EXCEPTION '% non-URL value(s) left in source_url', v_bad; END IF;

    SELECT count(*) INTO v_orphan FROM applications
     WHERE source_url IS NULL AND source_note IS NULL;
    IF v_orphan > 0 THEN
        RAISE WARNING '% row(s) carry neither a URL nor a note — fine mid-intake, not at rest', v_orphan;
    END IF;

    RAISE NOTICE 'OK — source_url holds URLs or NULL; source_note holds the reason';
END $$;

COMMIT;
