-- 011_resume_versions.sql — jobs_tracker_v2
--
-- ⛔ SCHEMA ONLY. NOTHING IS MIGRATED. NOTHING READS FROM THESE TABLES YET.
--
-- Prepares the tables the FORWARD architecture needs (CLAUDE.md, "the database
-- becomes the source"). 010 built `resume_bullets` as a DERIVED index parsed out of
-- the résumé files, which is the correct current state. These tables are what a seat
-- looks like once a résumé is a SELECTION rather than a sixth copy of his career.
--
-- Creating them now costs nothing and blocks nothing. The migration of content, and
-- the round-trip proof that must precede it, happen later and deliberately.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/011_resume_versions.sql
--
-- Idempotent.

\set ON_ERROR_STOP on
BEGIN;

-- ── A résumé version: the master, or one seat's tailored set ─────────────────
CREATE TABLE IF NOT EXISTS resume_versions (
    id             serial PRIMARY KEY,
    application_id integer REFERENCES applications(id) ON DELETE CASCADE,  -- NULL = master
    label          text NOT NULL,
    sent_at        timestamptz,        -- non-null = frozen; see the trigger below
    note           text,
    created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS resume_versions_label ON resume_versions (label);

-- ── Which bullets a version uses, in what order, with per-seat edits ─────────
-- A seat is a SELECTION WITH EDITS. Before this, six full copies of his career sat
-- across the workspaces, all diverged, every one going stale silently when the master
-- changed — the duplication CLAUDE.md records removing at the master level, recreated
-- one level down.
CREATE TABLE IF NOT EXISTS resume_version_bullets (
    version_id    integer NOT NULL REFERENCES resume_versions(id) ON DELETE CASCADE,
    bullet_id     integer NOT NULL REFERENCES resume_bullets(id),
    section_id    text NOT NULL,
    ord           integer NOT NULL,
    override_text text,               -- NULL = use the library bullet unchanged
    override_html text,
    PRIMARY KEY (version_id, section_id, ord),
    CONSTRAINT override_both_or_neither
        CHECK ((override_text IS NULL) = (override_html IS NULL))
);

-- ── A sent résumé is history, not a working document ────────────────────────
-- He asked for rewriting a sent résumé to be IMPOSSIBLE, not merely discouraged.
-- Three seats were already sent on 26 August; a later master change must never
-- rewrite what an employer actually received.
CREATE OR REPLACE FUNCTION refuse_edit_of_sent_resume() RETURNS trigger AS $$
DECLARE v_sent timestamptz; v_label text;
BEGIN
    SELECT sent_at, label INTO v_sent, v_label
      FROM resume_versions WHERE id = COALESCE(NEW.version_id, OLD.version_id);
    IF v_sent IS NOT NULL THEN
        RAISE EXCEPTION
            'resume version "%" was sent on % — it is history, not a working document. '
            'Create a new version alongside it rather than editing what went out.',
            v_label, v_sent;
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS resume_version_bullets_frozen ON resume_version_bullets;
CREATE TRIGGER resume_version_bullets_frozen
    BEFORE INSERT OR UPDATE OR DELETE ON resume_version_bullets
    FOR EACH ROW EXECUTE FUNCTION refuse_edit_of_sent_resume();

-- ── Leading-verb uniqueness, enforced on the master ─────────────────────────
-- Verified 2026-08-26 against the live table: master experience carries 39 bullets
-- and 39 distinct leading verbs, so this holds today. CLAUDE.md: the free-verb list
-- "has been wrong before — never trust it, regenerate from the file". Here it stops
-- being a warning and becomes a constraint.
CREATE UNIQUE INDEX IF NOT EXISTS resume_bullets_master_verb_unique
    ON resume_bullets (lower(leading_verb))
    WHERE source = 'master' AND section_kind = 'experience' AND leading_verb IS NOT NULL;

-- ── Hygiene: reported, not enforced ────────────────────────────────────────
-- The master carries 4 bullets with no <strong> and 12 with no digit. The digit test
-- is too strict anyway — a spelled number or a scale marker satisfies the rule — so
-- these surface as findings rather than blocking a write.
CREATE OR REPLACE VIEW resume_hygiene AS
SELECT source, section_id, ord, leading_verb, word_count,
       NOT has_bold   AS missing_bold,
       NOT has_number AS missing_number,
       left(text, 70) AS preview
  FROM resume_bullets
 WHERE section_kind = 'experience' AND (NOT has_bold OR NOT has_number);

DO $$
DECLARE v integer;
BEGIN
    SELECT count(*) INTO v FROM information_schema.tables
     WHERE table_name IN ('resume_versions','resume_version_bullets');
    IF v <> 2 THEN RAISE EXCEPTION 'expected 2 tables, found %', v; END IF;
    IF (SELECT count(*) FROM resume_versions) > 0 THEN
        RAISE NOTICE 'NOTE: resume_versions already holds rows — not added by this migration';
    END IF;
    RAISE NOTICE 'OK — version tables ready. NOTHING MIGRATED. Files remain the source.';
END $$;

COMMIT;
