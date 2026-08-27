-- 012_resume_master_source.sql — jobs_tracker_v2
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/012_resume_master_source.sql
--
-- ============================================================================
-- ⚑ THE DIRECTION FLIPS — FOR THE MASTER RÉSUMÉ, AND ONLY FOR IT. 2026-08-27.
-- ============================================================================
--
-- His words, 2026-08-27: "remember, you SHOULD be using a DB to store the
-- information", "AND prepare the HTML from that DB", "starting now, we do that",
-- "from the master resume". That closes the deferral recorded in
-- db/DESIGN-bullets.md ("⛔ NOT YET IMPLEMENTED") for one document.
--
-- WHAT THIS SUPERSEDES.  010_resume_bullets.sql opens with:
--
--     ⛔ THIS TABLE IS DERIVED. IT IS NEVER AUTHORED. EDITING A ROW CHANGES NOTHING.
--     upgrad_resume.html  ->  resume_bullets  ->  rendered pages / PDF / .docx
--
-- Migrations are history and 010 is not edited. Read it with this note beside it.
-- As of today the chain for the MASTER has one more link on the FRONT of it:
--
--     resume_documents + resume_roles + resume_sections + resume_blocks   ← AUTHORED
--                 |
--                 v   automation/resume_db.py generate
--        master/upgrad_resume.html                                       ← BUILD ARTEFACT
--                 |
--                 +--> automation/upgrad_apply.py  -> Hiration -> PDF
--                 +--> automation/jobs_sync.py --bullets -> resume_bullets  ← STILL DERIVED
--
-- So 010's sentence is still literally true of `resume_bullets`: it is derived,
-- it is never authored, and editing a row still changes nothing. What changed is
-- what sits UPSTREAM of the file it derives from. `resume_bullets` keeps its job —
-- the cross-seat comparison index over all seven résumés — and this migration does
-- not touch it, does not relax its NOT NULLs, and does not add `bullet_key` or
-- `retired_at` to it. Those belong on the authored table, and they are here, on
-- `resume_blocks`.
--
-- WHY A NEW TABLE RATHER THAN REPURPOSING `resume_bullets`.  One table cannot be
-- both "authored, for the master" and "derived, for six workspaces" without a mode
-- flag that every future reader has to remember. Worse, `jobs_sync.py --bullets`
-- DELETEs and re-INSERTs a source wholesale on every run — pointing the authored
-- master at that table would mean a routine sync could silently destroy the source
-- of truth. A separate table makes that impossible rather than discouraged, which
-- is the same reasoning migration 011 used for sent résumés.
--
-- ⚠ SCOPE. `doc_key = 'master'` is the only document this covers. The six per-seat
-- workspaces are untouched, their files are still authored by hand, and the
-- exporter is unchanged — not one line of `upgrad_apply.py` or
-- `upgrad_resume_paste.py` moves for this. DESIGN-bullets.md §6: "Migration is
-- per-workspace and incremental. There is no flag day."
--
-- ⚠ WHAT THE DATABASE STILL DOES NOT HOLD, stated out loud rather than implied.
-- `resume_certifications` is created and is EMPTY. His certifications live only in
-- the Hiration card (CLAUDE.md: "education, certifications and the pre-2016 roles
-- are card-only"), and `master/upgrad_resume.html` has no certifications section to
-- parse — the sole certification-shaped item in the file is the IIIT postgraduate
-- diploma, which is stored here as an EDUCATION row because that is where the file
-- puts it. An empty table with this note is the honest record; inventing rows to
-- make "the database is the source" sound complete is the shape of the bug
-- migration 007 paid for on `source_url`.
--
-- ⚠ `resume_bullets.word_count` IS COMPUTED BY THE WRONG COUNTER AND NOTHING HERE
-- ENFORCES ANYTHING ON IT.  `jobs_sync.hygiene()` used `len(text.split())`, the
-- naive splitter CLAUDE.md's measurement-traps section names by name: it counts a
-- standalone " — " as a word, so a 25-word bullet reports as 26. Measured against
-- the master on 2026-08-27: the naive rule flags 3 experience bullets over 25
-- words; CLAUDE.md's rule flags 0. DESIGN-bullets.md §4 proposed
-- `CHECK (word_count <= 25)` — against that column it would have rejected three
-- honest bullets and created pressure to trim them, which is exactly the failure
-- CLAUDE.md records ("Four bullets were trimmed that did not need trimming").
-- This migration therefore (a) puts the CORRECT counter in SQL as
-- `resume_word_count()`, (b) makes `resume_blocks.word_count` a GENERATED column
-- over it so it cannot be hand-set, and (c) enforces ≤25 only on that column.
-- `automation/jobs_sync.py` was corrected the same day to use the same rule.
--
-- Idempotent: safe to re-run. Creates nothing that exists, drops nothing at all,
-- and inserts no résumé content — `automation/resume_db.py load` does that.

\set ON_ERROR_STOP on
BEGIN;

-- ---------------------------------------------------------------------------
-- Derivation functions. Every hygiene fact about a bullet is computed FROM the
-- bullet, never stored beside it. DESIGN-bullets.md §9.9: "a word_count that
-- disagrees with text is the same class of bug as a paste sheet that disagrees
-- with the résumé — a second copy of a fact, free to drift."
-- ---------------------------------------------------------------------------

-- Tags dropped, entities unescaped, whitespace collapsed. Mirrors
-- `upgrad_resume_paste._cell()` deliberately, INCLUDING its no-separator rule:
-- inserting a space at every tag boundary turns "<strong>16 ms</strong>," into
-- "16 ms ," and inflates the word count with an orphaned comma.
--
-- The entity vocabulary is exactly the five the master uses (&mdash; &ndash;
-- &nbsp; &lt; &gt; &amp;). `resume_db.py load` REFUSES a file containing any
-- other named entity rather than letting an unknown one survive into `text`.
-- &amp; is expanded last, so "&amp;lt;" does not become "<".
CREATE OR REPLACE FUNCTION resume_plain(h text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
    SELECT btrim(regexp_replace(
             replace(replace(replace(replace(replace(replace(
               regexp_replace(h, '<[^>]+>', '', 'g'),
               '&mdash;', U&'\2014'),
               '&ndash;', U&'\2013'),
               '&nbsp;',  ' '),
               '&lt;',    '<'),
               '&gt;',    '>'),
               '&amp;',   '&'),
             '\s+', ' ', 'g'));
$$;

-- CLAUDE.md, measurement traps: "Count only tokens containing [A-Za-z0-9]."
-- A naive split() counts " — " as a word. This is the counter
-- `automation/hygiene_check.py:words()` uses, expressed once in SQL so the
-- constraint and the gate cannot disagree.
CREATE OR REPLACE FUNCTION resume_word_count(t text) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
    SELECT count(*)::int
      FROM regexp_split_to_table(t, '\s+') AS w
     WHERE w ~ '[A-Za-z0-9]';
$$;

-- The bullet's first word, punctuation stripped. NULL when there is none.
CREATE OR REPLACE FUNCTION resume_leading_verb(t text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
    SELECT (regexp_match(t, '[A-Za-z][A-Za-z''-]*'))[1];
$$;

-- ---------------------------------------------------------------------------
-- resume_documents — one row per résumé document. Today: 'master'.
-- ---------------------------------------------------------------------------
-- The chrome that is not career data and not a bullet: the head, the parser
-- contract comment, the operating instructions under the <h1>, and the two
-- headings and two notes that caption the card-only tables. It is stored rather
-- than hard-coded in the template for one reason — the template must be able to
-- reproduce the committed file BYTE FOR BYTE, and this text is part of the file.
--
-- ⚠ `contract_comment` currently says "YOU paste sections 1-15 into the Hiration
-- card by hand", which stops being true of a generated file. Rewriting it is a
-- content decision for him, not a migration's to make. It is stored verbatim.
CREATE TABLE IF NOT EXISTS resume_documents (
    doc_key             text PRIMARY KEY,

    title               text NOT NULL,          -- <title> and <h1>
    lang                text NOT NULL DEFAULT 'en',
    -- Relative from the document's own directory. DESIGN-bullets.md §2 names the
    -- stylesheet depth as the single per-workspace difference: '../style.css' at
    -- master/, '../../../style.css' at Month-YYYY/DD/<slug>/.
    stylesheet_href     text NOT NULL,
    favicon_href        text NOT NULL,
    -- CLAUDE.md's measurement traps: a wrong depth here left EVERY copy button on
    -- EVERY tailored résumé dead through six workspaces, because a missing script
    -- throws nothing. `resume_db.py generate` asserts the path resolves.
    script_src          text NOT NULL,

    contract_comment    text NOT NULL,          -- inside <!-- --> , verbatim
    intro_html          text NOT NULL,          -- the <p> under the <h1>, verbatim

    dates_heading       text NOT NULL,          -- <h2> over the roles table
    education_label     text NOT NULL DEFAULT 'Education',
    education_note_html text,                   -- "Never downgrade the MS." — an
                                                -- instruction to the reader of this
                                                -- file, NOT résumé content
    personal_heading    text NOT NULL,          -- <h2> over the personal table
    personal_note_html  text NOT NULL,          -- the <p> under it, verbatim

    updated_at          timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- resume_roles — the career, ONCE. First-class, not repeated per bullet.
-- ---------------------------------------------------------------------------
-- `resume_bullets` carries company/role_title/date_from/date_to/location on
-- EVERY row — 24 identical copies of the VoltusWave line for `quick-vp` alone.
-- Harmless in a derived index; wrong in a source of truth, and precisely the
-- duplication DESIGN-bullets.md exists to remove ("six full copies of his career
-- existed across workspaces… the same duplication recreated one level down").
--
-- It also removes a structural fragility: in `resume_bullets` a role is attached
-- only to its bullets, so a role with zero bullets loses its company, title,
-- dates and location entirely — there is no row left to hang them on.
CREATE TABLE IF NOT EXISTS resume_roles (
    doc_key            text NOT NULL REFERENCES resume_documents(doc_key) ON DELETE CASCADE,
    -- Row number in the résumé's own dates table, and the positional key the
    -- parser uses: the Nth experience section is role N.
    n                  integer NOT NULL CHECK (n >= 1),

    company            text NOT NULL,
    role_title         text NOT NULL,
    -- Free text, not dates. The file writes "Mar 2025" / "Apr 2026"; a date type
    -- would force a day nobody has and would render back differently.
    -- ⚠ These are what the FILE asserts. The dates on an exported PDF live in the
    -- Hiration card, which the bot never writes.
    date_from          text NOT NULL,
    date_to            text NOT NULL,
    location           text NOT NULL,

    -- The file bolds exactly one cell in this table: the current role's end date.
    -- CLAUDE.md, master/README.md and the export checklist all insist VoltusWave
    -- must read Apr 2026, and the bold is the file shouting it. A plain-text store
    -- drops it silently and it does not surface until an exported PDF. `resume_db.py
    -- load` RAISES on markup in any other cell rather than discarding it.
    date_to_emphasised boolean NOT NULL DEFAULT false,

    PRIMARY KEY (doc_key, n)
);

-- ---------------------------------------------------------------------------
-- resume_education — a CLAUDE.md fixed fact, previously unstorable
-- ---------------------------------------------------------------------------
-- "Education = MS in Computer Science, University of Houston. Never downgrade it.
-- The IIIT postgraduate diploma in AI/ML coexists but is not the highest degree."
-- It appears on the exported PDF and `resume_bullets` had no row for it —
-- `section_kind`'s CHECK would have REJECTED one.
CREATE TABLE IF NOT EXISTS resume_education (
    doc_key     text NOT NULL REFERENCES resume_documents(doc_key) ON DELETE CASCADE,
    ord         integer NOT NULL CHECK (ord >= 1),
    credential  text NOT NULL,          -- "MS Computer Science"
    institution text NOT NULL,          -- "University of Houston"
    date_range  text NOT NULL,          -- "Aug 2004 – Dec 2007" / "Jan 2021"
    -- Exactly one row per document may be the highest degree. The partial unique
    -- index below makes "never downgrade the MS" a property of the schema.
    is_highest  boolean NOT NULL DEFAULT false,
    PRIMARY KEY (doc_key, ord)
);

CREATE UNIQUE INDEX IF NOT EXISTS resume_education_one_highest
    ON resume_education (doc_key) WHERE is_highest;

-- ---------------------------------------------------------------------------
-- resume_certifications — CREATED EMPTY, AND THAT IS THE POINT
-- ---------------------------------------------------------------------------
-- CLAUDE.md and master/README.md both name certifications; the file contains
-- none, and neither does `resume_bullets`. They exist only in the Hiration card,
-- hand-edited there, and the bot never touches them. This table is the place they
-- go if they are ever brought in, and until then its emptiness is the record that
-- "the database is the source" is a claim about the master FILE, not about every
-- fact on the exported PDF.
CREATE TABLE IF NOT EXISTS resume_certifications (
    doc_key     text NOT NULL REFERENCES resume_documents(doc_key) ON DELETE CASCADE,
    ord         integer NOT NULL CHECK (ord >= 1),
    name        text NOT NULL,
    issuer      text,
    awarded     text,
    -- TRUE while the certification exists only in the Hiration card and no
    -- generated artefact renders it.
    card_only   boolean NOT NULL DEFAULT true,
    note        text,
    PRIMARY KEY (doc_key, ord)
);

-- ---------------------------------------------------------------------------
-- resume_profile — Personal Information, the four values
-- ---------------------------------------------------------------------------
-- Hyderabad · +91 93640 27487 · abhisheik@abhideo.ai · abhisheikdeo. Verified on
-- every exported PDF, and CLAUDE.md records the LinkedIn slug as one of this
-- repo's measurement traps ("lives in a PDF LINK ANNOTATION, not extractable
-- text… a text-only grep reads abhisheikdeo as missing on a perfectly good PDF").
-- `role_table()` deliberately ignores this table, so none of it ever reached
-- `resume_bullets`.
--
-- `value_html` is verbatim so the <strong> on Hyderabad and on the slug, and the
-- <code>abhideo</code> gloss beside it, survive. `value_text` is derived.
CREATE TABLE IF NOT EXISTS resume_profile (
    doc_key     text NOT NULL REFERENCES resume_documents(doc_key) ON DELETE CASCADE,
    ord         integer NOT NULL CHECK (ord >= 1),
    field_label text NOT NULL,
    value_html  text NOT NULL,
    value_text  text GENERATED ALWAYS AS (resume_plain(value_html)) STORED,
    PRIMARY KEY (doc_key, ord)
);

-- ---------------------------------------------------------------------------
-- resume_sections — the fifteen sections, in file order
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resume_sections (
    doc_key        text NOT NULL REFERENCES resume_documents(doc_key) ON DELETE CASCADE,
    -- File order. Also the number the <h2> prints: "6. VoltusWave — …".
    ord            integer NOT NULL CHECK (ord >= 1),
    -- ⛔ THE TEN `quick-*` IDS ARE A CONTRACT. `upgrad_apply.py` parses by id and
    -- master/README.md records the trap: a misspelt id is SKIPPED SILENTLY and the
    -- export still looks successful. `resume_db.py generate` asserts all ten are
    -- present and non-empty before it writes anything.
    section_id     text NOT NULL,
    section_kind   text NOT NULL
        CHECK (section_kind IN ('headline', 'summary', 'skills', 'experience')),
    -- The <h2> inner HTML with the leading "N. " removed — verbatim otherwise,
    -- entities included ("Skills — Technology Leadership &amp; Strategy"), and
    -- including the trailing "— card-only" and El Paso's "· THE JAVA YEARS".
    -- It is the file's own wording; rewriting it here would be the derived layer
    -- editorialising over its source.
    heading_html   text NOT NULL,
    -- The five pre-2016 roles the exporter never writes. They are on the résumé,
    -- he reads them, and CLAUDE.md's verb-uniqueness rule counts their verbs.
    card_only      boolean NOT NULL DEFAULT false,
    -- Which role this section's bullets belong to. NULL off the experience kinds.
    role_n         integer,

    PRIMARY KEY (doc_key, section_id),
    -- The composite target `resume_blocks` points at, so a block's `section_kind`
    -- cannot drift from its section's. Denormalised on purpose and made
    -- undriftable by PostgreSQL rather than by a convention.
    UNIQUE (doc_key, section_id, section_kind),
    UNIQUE (doc_key, ord),
    CONSTRAINT resume_sections_role_fk
        FOREIGN KEY (doc_key, role_n) REFERENCES resume_roles(doc_key, n),
    CONSTRAINT resume_sections_role_only_on_experience
        CHECK ((section_kind = 'experience') = (role_n IS NOT NULL))
);

-- ---------------------------------------------------------------------------
-- resume_blocks — THE AUTHORED BULLETS. This is the source of truth.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resume_blocks (
    doc_key      text NOT NULL,
    section_id   text NOT NULL,
    section_kind text NOT NULL,
    -- Position within the section, 1-based, in file order.
    ord          integer NOT NULL CHECK (ord >= 1),

    -- ⛔ `ord` IS NOT THE KEY. DESIGN-bullets.md §2: re-ordering the master would
    -- silently re-point every seat's selection at a different bullet. `bullet_key`
    -- is the stable identity a per-seat selection references — 'vp-kinesis-two-stream'
    -- — and it survives re-ordering, re-wording and re-sectioning.
    bullet_key   text NOT NULL,

    -- ⛔ THE AUTHORED FIELD, AND THE ONLY ONE. Verbatim inner HTML of the <p>,
    -- exactly the bytes between "<p>" and "</p>" in the file — entities in the
    -- spelling the file uses (&mdash; stays &mdash;, a literal — stays literal).
    --
    -- Storing the SUBSTRING rather than a re-serialised parse tree is what makes
    -- the round trip byte-identical. A BeautifulSoup round trip is lossless in
    -- substance but not in spelling: `str()` on a text node re-escapes nothing, so
    -- "&amp;" in a bare text node comes back a bare "&", and "&lt;strong&gt;" comes
    -- back as a REAL <strong> tag — a silent injection that a second round-trip
    -- check cannot see, because it is stable thereafter.
    html         text NOT NULL CHECK (html <> ''),

    -- Everything below is DERIVED FROM `html` and cannot be written.
    text         text GENERATED ALWAYS AS (resume_plain(html)) STORED,
    word_count   integer GENERATED ALWAYS AS (resume_word_count(resume_plain(html))) STORED,
    has_bold     boolean GENERATED ALWAYS AS (html ~* '<(strong|b)\y') STORED,
    -- Mechanical proxy: a digit or a %. CLAUDE.md's rule is "a number, %, scale
    -- marker, or measurable outcome" and the last two are human judgement. FALSE
    -- is a real miss worth a look; TRUE is not a pass, and never a reason to add
    -- a number.
    has_number   boolean GENERATED ALWAYS AS (resume_plain(html) ~ '[0-9%]') STORED,
    -- NULL off the experience sections: "unique leading verb" is a rule about
    -- experience bullets, and a NULL keeps a naive query from counting
    -- "Technology" out of the skills block as a verb.
    leading_verb text GENERATED ALWAYS AS (
        CASE WHEN section_kind = 'experience'
             THEN resume_leading_verb(resume_plain(html)) END) STORED,

    -- ⛔ A bullet LEAVES the master by being retired, never by being deleted.
    -- A sent seat may still reference it and history must stay readable.
    retired_at   timestamptz,

    created_at   timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (doc_key, section_id, ord),
    UNIQUE (doc_key, bullet_key),
    CONSTRAINT resume_blocks_section_fk
        FOREIGN KEY (doc_key, section_id, section_kind)
        REFERENCES resume_sections (doc_key, section_id, section_kind)
        ON DELETE CASCADE,

    -- Hygiene, per CLAUDE.md, as constraints rather than warnings. Every one was
    -- run as a SELECT against the real master before being enforced
    -- (DESIGN-bullets.md §7 step 4): 0 rejections on all three.
    --
    -- ≤25 words — EXPERIENCE ONLY. The summary is prose and legitimately long;
    -- the skills block is capability labels, not sentences.
    CONSTRAINT resume_blocks_word_cap
        CHECK (section_kind <> 'experience' OR word_count <= 25),
    -- ≥1 bolded fact. Load-bearing: the paste source must carry it, because a
    -- hand-dragged selection loses bold and that does not surface until the PDF.
    CONSTRAINT resume_blocks_bold
        CHECK (section_kind <> 'experience' OR has_bold),
    -- No trailing period on a bullet. The summary legitimately ends in one.
    CONSTRAINT resume_blocks_no_trailing_period
        CHECK (section_kind <> 'experience' OR text !~ '\.$')
    -- ⛔ has_number is DELIBERATELY NOT a constraint. "Scale marker or measurable
    -- outcome" is human judgement, and a CHECK on the proxy would reject honest
    -- bullets and create pressure to INVENT a number — the cardinal sin here.
    -- 11 of 64 experience bullets are has_number = false today, all legitimately.
);

-- Leading-verb uniqueness across ALL TEN roles, card-only sections included.
-- ⚠ HALF THE RULE. CLAUDE.md: "same-root collisions count, and they hide
-- mid-bullet" — `Lifted` sat beside "lifting sales" until 2026-08-25, and
-- Architected ≈ Architecting. A UNIQUE index catches exact repeats only; the stem
-- check stays a query (db/README.md, and hygiene_check.py runs it). Do not let
-- this index create the impression the rule is fully enforced.
CREATE UNIQUE INDEX IF NOT EXISTS resume_blocks_verb_unique
    ON resume_blocks (doc_key, lower(leading_verb))
 WHERE section_kind = 'experience' AND retired_at IS NULL AND leading_verb IS NOT NULL;

CREATE INDEX IF NOT EXISTS resume_blocks_section
    ON resume_blocks (doc_key, section_id, ord);

COMMENT ON TABLE resume_blocks IS
    'AUTHORED. The master résumé''s bullets, and the source of truth for them as of '
    '2026-08-27. master/upgrad_resume.html is generated FROM this table by '
    'automation/resume_db.py and is a build artefact — do not hand-edit it. '
    'Contrast resume_bullets, which stays a DERIVED cross-seat index (see 010).';
COMMENT ON COLUMN resume_blocks.html IS
    'Verbatim inner HTML of the <p>, byte-for-byte as the file writes it. The only '
    'authored column; everything else on the row is generated from it.';
COMMENT ON COLUMN resume_blocks.bullet_key IS
    'Stable identity. NOT ord — re-ordering the master must not re-point a seat''s selection.';
COMMENT ON TABLE resume_roles IS
    'The career once, not once per bullet. resume_bullets repeats these five columns '
    'on every row; that is fine for a derived index and wrong for a source.';
COMMENT ON TABLE resume_certifications IS
    'Deliberately EMPTY. His certifications live only in the Hiration card and are not '
    'in master/upgrad_resume.html. The emptiness is the record of that boundary.';

-- ---------------------------------------------------------------------------
-- Prove the shape, or refuse to commit.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  missing text;
  n_gen   bigint;
  n_chk   bigint;
BEGIN
  SELECT string_agg(t, ', ') INTO missing
    FROM unnest(ARRAY['resume_documents','resume_roles','resume_education',
                      'resume_certifications','resume_profile','resume_sections',
                      'resume_blocks']) AS t
   WHERE to_regclass('public.' || t) IS NULL;
  IF missing IS NOT NULL THEN
    RAISE EXCEPTION 'missing table(s): %', missing;
  END IF;

  -- The derived columns must be GENERATED, not merely present. A writable
  -- word_count is the drift this design exists to remove.
  SELECT count(*) INTO n_gen FROM information_schema.columns
   WHERE table_name = 'resume_blocks'
     AND column_name IN ('text','word_count','has_bold','has_number','leading_verb')
     AND is_generated = 'ALWAYS';
  IF n_gen <> 5 THEN
    RAISE EXCEPTION 'resume_blocks: expected 5 GENERATED columns, found %', n_gen;
  END IF;

  SELECT count(*) INTO n_chk FROM pg_constraint
   WHERE conrelid = 'resume_blocks'::regclass AND contype = 'c'
     AND conname IN ('resume_blocks_word_cap','resume_blocks_bold',
                     'resume_blocks_no_trailing_period');
  IF n_chk <> 3 THEN
    RAISE EXCEPTION 'resume_blocks: expected 3 hygiene CHECKs, found %', n_chk;
  END IF;

  IF to_regclass('public.resume_blocks_verb_unique') IS NULL THEN
    RAISE EXCEPTION 'the leading-verb uniqueness index is missing';
  END IF;

  -- The counter must be CLAUDE.md's, not split(). " — " is not a word.
  IF resume_word_count('Cut cost 25 — 30% — measured') <> 5 THEN
    RAISE EXCEPTION 'resume_word_count is counting punctuation tokens';
  END IF;
  IF resume_plain('<p>A &amp; B<strong>C</strong></p>') <> 'A & BC' THEN
    RAISE EXCEPTION 'resume_plain is not matching upgrad_resume_paste._cell()';
  END IF;

  RAISE NOTICE 'OK — the master résumé has a home. Populate with: automation/.venv/bin/python automation/resume_db.py load';
END $$;

COMMIT;
