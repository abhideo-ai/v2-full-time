# Planned: the database as the source for résumé bullets

> # ⛔ NOT YET IMPLEMENTED
>
> **Nothing in this document describes how the workspace works today.** As of 2026-08-26 the
> résumé files are still the source of truth, `automation/upgrad_apply.py` still exports by
> reading `<workspace>/upgrad_resume.html`, and the one table that exists — `resume_bullets`
> — is a **derived, read-only index** that nothing reads yet.
>
> This is a plan for a future session. It was written after the round-trip proof below was run
> against all seven real résumés, so the numbers in §1 are measured, not estimated.

His words, 2026-08-26:

> 1. master resume has it's own bullets in a table
> 2. you retrieve them, compare them to the JD
> 3. score & improve
> 4. new bullets are stored in the DB again
> 5. using these DB bullets, you export the PDF from upgrad
> 6. I only see the final PDF. if any changes are needed, you can make those changes to the DB
> 7. we could perhaps have a HTML page that helps us with comparison, etc. all of these run from the DB itself
> 8. HTML is no longer static. it's dynamic.

…and, deferring it: *"we can implement this AFTER we're done… GOING forward, we do that."*

**The problem it solves.** Six full copies of his career exist across workspaces, all diverged.
When the master changes, all six go stale silently. That is the exact duplication CLAUDE.md
records removing at the master level on 2026-08-25 — a parsed copy, a hand-paste copy and a
blank template whose sections *"were duplicated verbatim and drifting apart silently"* — recreated
one level down.

---

## 1. THE ROUND-TRIP PROOF — run 2026-08-26, and it is clean

This is the question that decides whether any of the rest is safe: **can the master's 39 hand-built
bullets survive a parse and come back intact?** If the parse silently drops a `<strong>`, the loss
does not surface until an exported PDF has no bold in it.

Method: parse each résumé into `resume_bullets`, regenerate the HTML from the table, diff against
the original. Harness kept at `scratchpad/roundtrip.py` (read-only; it never wrote to a résumé).

### Result — 7 files, 488 bullets

| outcome | count |
|---|---|
| bullet HTML **byte-identical** | **458** |
| differs, **entity form only** (`&mdash;` → `—`) | 30 |
| differs in text, tags or attributes | **0** |
| bullets lost, gained or reordered | **0** |
| sections in the file the parser missed | **0** |

**`<strong>` counts are preserved exactly on every file** — 117 → 117 on the master, and likewise
on all six workspaces. **Bold is not at risk.**

### Every difference, enumerated

There are exactly two classes, and only two.

**(a) Entity form — 30 bullets.** `&mdash;` becomes a literal `—`, `&ndash;` becomes `–`.
BeautifulSoup parses the entity to its character and re-serialises with the `minimal` formatter,
which only re-escapes `&`, `<` and `>`. Same character, same rendering, different spelling.
`&amp;` round-trips **byte-identically** — 95 bullets containing `&amp;` and nothing else came
back unchanged, so the `&` case is not affected.

**(b) Indentation — 5 lines on the master.** The master's own indentation is inconsistent: the
summary `<p>` sits at 4 spaces and the four Amura bullets (lines 141–144) at 6, while everything
else is at 2. A generator emits one canonical indent, so those lines move.

Nothing else differs. There is **no `&nbsp;` and no U+00A0 anywhere** in any of the seven files,
which removes the nastiest class of invisible corruption before it starts.

### The trap: byte-identity is NOT reachable, and chasing it makes things worse

The obvious fix for (a) is to serialise with `formatter="html"`, which emits named entities.
**Tested, and it is worse: 75 bullets differ instead of 30.** The files mix the two spellings —
some em-dashes are written `&mdash;`, others are literal `—`, and `·` is always literal. Entity
form over-escapes the literals; minimal form under-escapes the entities. **No formatter reproduces
a file that is internally inconsistent.**

**Recommendation: normalise once, then byte-identity holds forever.** Take the `minimal` output
(literal characters) as canonical, commit that normalisation to the master as its own reviewed
diff — 3 bullet lines and 5 indentation lines, reviewable in a minute — and from then on
*generated output equals committed file, byte for byte*. That normalisation is a **prerequisite
step of the migration, not a side effect of it**, and it must be a commit he can read.

### What this proof does and does not license

- ✅ The parse is **lossless in substance**. Text, tags, bold, order, counts: all exact.
- ✅ Committing to the database as the source is **safe on the evidence**.
- ⚠ It proves the parse of *these seven files as they stand today*. Re-run it as the last gate
  before the cutover, because the two in-flight workspaces are still being written.
- ⛔ It says nothing about whether Hiration renders the result identically. That is a **separate
  gate**: export one seat both ways and diff the PDFs (§7, step 6).

---

## 2. Schema

Four tables. `resume_bullets` already exists as a derived index and is **repurposed**, not
replaced — same columns, opposite direction of truth.

### `resume_bullets` — the master's career, one row per bullet

This becomes the source. Today's columns already carry what is needed (`section_id`,
`section_kind`, `section_label`, `card_only`, `company`, `role_title`, `date_from`, `date_to`,
`location`, `ord`, `text`, `html`, `leading_verb`, `word_count`, `has_bold`, `has_number`).
Changes required:

- Drop `source`, `source_path`, `source_sha256` — a source *file* is no longer the origin.
  Keep them on the import path only (§7 step 2), then remove in a later migration once the
  cutover is proven. **Do not remove them in the same migration that flips the direction**;
  they are the evidence trail back to the file.
- Add `bullet_key text UNIQUE` — a stable identifier (`vp-kinesis-two-stream`) so a per-seat
  selection survives re-ordering. **`ord` must not be the key**: re-ordering the master would
  silently re-point every seat's selection at a different bullet.
- Add `retired_at timestamptz` — a bullet leaves the master by being retired, never deleted.
  A sent seat may still reference it, and history must stay readable.
- `html` is the authored field; `text`, `word_count`, `has_bold`, `has_number` and `leading_verb`
  are **generated columns or trigger-maintained**, never hand-set. They are facts about `html`,
  and letting them be written independently recreates drift inside one row.

### `resume_seats` — one row per seat's résumé

| column | why |
|---|---|
| `application_id` → `applications(id)` | the seat |
| `template_id` → `resume_templates(id)` | which document shell to render into |
| `state` `draft \| exported \| sent` | drives the immutability gate in §5 |
| `sent_at`, `sent_sha256`, `sent_pdf_path` | what actually went out |
| `generated_at`, `generated_path` | the build artefact's provenance |

### `resume_seat_bullets` — the selection, with edits

**A seat is a selection with overrides, not a copy of his career.** One row per bullet a seat uses:

| column | why |
|---|---|
| `seat_id` → `resume_seats(id)` | |
| `bullet_key` → `resume_bullets(bullet_key)` | what it is derived FROM |
| `section_id`, `ord` | where it lands in this seat's résumé |
| `html_override` | NULL = use the master's `html` verbatim. Non-NULL = Rule 7 re-vectoring |
| `override_reason` | required when `html_override` is set — a `CHECK` enforces it |

`override_reason` being NOT NULL whenever `html_override` is is the same shape as `./todo`
refusing to move a task out with no reason. A re-vectored bullet with no recorded reason is
how a seat's résumé becomes unexplainable six weeks later.

**Consequence worth stating plainly:** a master edit propagates to every draft seat that did not
override that bullet, and to none that did. That is the entire point.

### `resume_templates` — the document shell

The chrome around the sections: doctype, head, the dates table, the `<h2>` headings, the closing
script tag. Stored **with `{{BULLETS:<section_id>}}` placeholders** where each section's body goes.

This is the design decision that makes the round-trip clean, and it is worth being explicit about
why: **the generator substitutes bullets into a stored shell rather than composing a document from
scratch.** Everything that is not a bullet is preserved byte-for-byte because it is never
regenerated. The blast radius of a generator bug is confined to exactly the thing the database
owns.

One template serves every seat. The single per-workspace difference is the stylesheet depth
(`href="../style.css"` at `master/`, `href="../../../style.css"` at `Month-YYYY/DD/<slug>/`),
which `resume.py new` already rewrites and the generator does the same way.

---

## 3. Generating `upgrad_resume.html`

```
automation/resume_render.py --slug <slug>     # or --master
```

Writes `<workspace>/upgrad_resume.html`. **The exporter does not change at all.** The file stops
being authored and becomes a **build artefact** — like a compiled binary. Nobody edits it; it is
regenerated on demand.

Rules the generator must hold, each for a reason already paid for once:

1. **The ten parsed section ids are a contract.** `quick-headline`, `quick-summary`,
   `quick-skills-{tls,ee,bd}`, `quick-vp`, `quick-deque`, `quick-rocket`,
   `quick-voltuswave-cofounder`, `quick-teletext`. `upgrad_apply.py` parses by id, and
   `master/README.md` records the trap: **a misspelt id is skipped silently and the export still
   looks successful.** The generator must assert all ten are present and non-empty before writing,
   and refuse otherwise.
2. **Every bullet is a standalone `<p>`, never a `<ul><li>`.** upGrad strips bold from list-rooted
   content.
3. **Experience order is fixed** and maps to the editor's `PR-child-0..4`.
4. **The five card-only sections still render** (`p-cura`, `p-innroad`, `p-mcd`, `p-elpaso`,
   `p-lynton`). The bot never writes them, but he reads the file, and CLAUDE.md's verb-uniqueness
   rule counts their leading verbs.
5. **Write atomically** — temp file, then rename. A generator interrupted halfway through the
   file he is about to export from is a worse failure than not running at all.
6. **Refuse to overwrite a file that is not a generated artefact.** Check for a generator
   provenance marker in the header; if it is absent, the file was hand-authored and has not been
   migrated. Refuse and say so.

---

## 4. Hygiene rules that become real constraints

CLAUDE.md says of the free-verb list: *"Never trust this list — regenerate it from the file."*
In a database that stops being a warning and becomes a constraint. These are the rules that are
mechanically decidable:

| rule | as a constraint | notes |
|---|---|---|
| ≤25 words | `CHECK (word_count <= 25)` | **experience bullets only.** The summary is prose and legitimately long; the skills block is capability labels |
| ≥1 bolded fact | `CHECK (has_bold)` on experience | the paste source must carry it |
| no trailing period | `CHECK (text !~ '\.$')` | |
| ≥1 number / % | `CHECK (has_number)` — **advisory, do not enforce** | see below |
| leading verb unique across all ten roles | `UNIQUE` index on `lower(leading_verb)` where `section_kind='experience' AND retired_at IS NULL` | |

**Two cautions, both load-bearing.**

*Do not enforce `has_number`.* CLAUDE.md's rule is *"≥1 number, %, scale marker, or measurable
outcome"* and the last two are human judgement. The column is a mechanical proxy: a `false` is a
real miss worth looking at, a `true` is not a pass. A `CHECK` on it would reject honest bullets
and, worse, create pressure to invent a number — which is the cardinal sin in this repo.

*Verb uniqueness needs a same-root check the database cannot express.* CLAUDE.md is explicit that
*"same-root collisions count, and they hide mid-bullet"* — `Lifted` as a leading verb sat beside
*lifting sales* until 2026-08-25, and `Architected ≈ Architecting`. A `UNIQUE` index catches exact
repeats only. The stem check stays a **query run at review time** across `text` of *all* rows,
skills block included, and it is one of the queries in §8. Do not let the constraint's existence
create the impression the rule is fully enforced.

**Per-seat overrides must satisfy the same constraints**, computed on the override rather than the
master row. A seat is where Rule 7 re-vectoring happens, so it is exactly where a 30-word bullet
would otherwise slip in.

---

## 5. Sent résumés are immutable — and it is structural, not a convention

Three seats have already been sent:

| slug | applied |
|---|---|
| `yes-madam-lead-architect` | 26 Aug 11:37 |
| `o9-senior-architect-agentic` | 26 Aug 12:19 |
| `wolters-kluwer-principal-ai-platform-engineer` | 26 Aug 12:35 |

**A résumé that went to an employer is a historical record, not a working document.** A recruiter
holds a specific PDF. Regenerating over it would leave the workspace describing a document that
was never sent, and CLAUDE.md's no-scrub rule is built on exactly this reasoning: removing a claim
*"does not unsend it — it only creates a gap between the version a recruiter holds and the version
they would see next."*

How the schema makes rewriting impossible rather than discouraged:

1. **`resume_seats.state` reaches `sent` and a `BEFORE UPDATE`/`BEFORE DELETE` trigger on
   `resume_seat_bullets` raises** for any seat in that state. Not application logic — a generator
   run by a future agent that has never read this file must fail, loudly, at the database.
2. **A `CHECK` binds the columns**: `state='sent'` requires `sent_at`, `sent_sha256` and
   `sent_pdf_path` all non-NULL. A seat cannot be marked sent without recording what was sent.
3. **`sent_sha256` is the digest of the exact `upgrad_resume.html` that produced the sent PDF**,
   captured at send time. It is the tamper-evidence: regenerate later, compare, and any drift is
   visible rather than inferred.
4. **Revision is by new version, never by edit.** Re-applying to the same seat clones the seat row
   to `revision = n+1` in `draft`, leaving revision *n* sealed. The generator writes
   `Abhisheik_Deo_Resume_v2.pdf` alongside, never over.
5. **The generator refuses a sent seat by default** and says which PDF was sent and when. A
   `--new-revision` flag is the only way past, and it creates a revision rather than overwriting.

⚠ **Do not assume a sent seat has a PDF at the predictable path.** `wolters-kluwer` is `applied`
with **no `Abhisheik_Deo_Resume.pdf` in its workspace** — its `document` event points at the
directory, and what was sent went out another way. The migration must record `sent_pdf_path` as
NULL-and-explained for that seat rather than inventing a path that does not exist. This is exactly
the shape of the `source_url` bug that cost migration 007: manufacturing a plausible value for a
column instead of recording that there is none.

---

## 6. Backward compatibility

**Migration is per-workspace and incremental. There is no flag day.**

| requirement | how it holds |
|---|---|
| `upgrad_apply.py` keeps working unchanged | it parses `upgrad_resume.html` by id. Whether that file was typed or generated is invisible to it. **Not one line of the exporter changes.** |
| an unmigrated workspace still exports | its file is hand-authored and simply stays that way. The generator refuses to touch a file with no provenance marker (§3 rule 6), so the two paths cannot collide |
| PostgreSQL down ⇒ he can still export | **the generated file is on disk.** The exporter never opens a database. A database outage blocks *regenerating*, not *exporting* — the same philosophy as `serve.py` down meaning the daily log falls back to localStorage and says so |
| migration is reversible | the generated file *is* the rollback. Revert the code, keep the files, and the workspace is exactly as it was. The precedent is 003 → 006: reversal was clean because the prior state was preserved rather than overwritten. Keep `source_path` / `source_sha256` until the cutover is proven (§2) |
| existing artefacts keep working | the six `upgrad_resume.html` files, the exported PDFs, the paste sheets and the launcher are all untouched. `resume.py sheet` still generates from the file, which is now generated from the database — one more link in the same chain, same direction |

### How to VERIFY backward compatibility — not assert it

Four tests, in `automation/tests/`:

1. **Round-trip.** Parse every résumé, regenerate, assert 0 text/tag/attribute differences and
   equal `<strong>` counts. Fails the build if a future parser change becomes lossy. This is §1
   turned into a permanent gate.
2. **Unmigrated export.** Point `upgrad_resume_paste.parse_slug` at a workspace with no database
   rows at all and assert all ten sections parse. Proves the old path is untouched.
3. **Database unreachable.** Run the export path with `JOBS_TRACKER_DSN` pointed at a database
   that does not exist and assert it still parses and would export. `automation/tests/run.sh`
   already does exactly this for the launcher's 503 path on port 8108 — same trick, and it is
   the reason that test is worth copying rather than inventing.
4. **Sent-seat immutability.** Attempt an `UPDATE` on a sent seat's bullets and assert the
   database raises. Attempt a generator run against a sent seat and assert it refuses.

---

## 7. Migration order, and what to verify at each step

Each step is reversible and verified before the next begins.

| # | step | verify |
|---|---|---|
| 1 | **Normalise entity spelling in the master** (§1). One reviewed commit, ~8 lines | he reads the diff; `<strong>` count unchanged; export one PDF and confirm bold |
| 2 | **Import** master + six workspaces via `jobs_sync.py --bullets` (exists, works) | 488 rows, 0 losses — the §1 proof, re-run |
| 3 | **Round-trip gate.** Regenerate all seven, diff | byte-identical after step 1. **If not, STOP** |
| 4 | **Add `bullet_key`, `retired_at`, the three new tables and the constraints** | constraints pass against real data *before* being enforced — run them as `SELECT`s first and look at what they would reject |
| 5 | **Generator**, against `master/` only | generated == committed, byte for byte |
| 6 | **⚠ The Hiration gate.** Export ONE unsent seat from the generated file and diff the PDF against the last one exported from the hand-authored file | identical bold, identical text, ≤3 pages. **This is the gate the round-trip cannot cover** |
| 7 | **Migrate the three unsent seats** — `principal-architect-ai-native`, `wipro-principal-software-architect`, `modmed-senior-software-architect` | each regenerates byte-identically; each still exports |
| 8 | **Migrate the three sent seats, read-only**, sealed at `state='sent'` with the captured digest | the immutability trigger fires; `wolters-kluwer`'s missing PDF is recorded as absent, not invented |
| 9 | **Then, and only then**, the comparison page and the `.docx` writer | — |

Steps 1–3 are the whole risk. Everything after them is ordinary work.

---

## 8. Queries worth having on day one

```sql
-- His question: the bullets one seat used for the VoltusWave role.
select ord, coalesce(sb.html_override, b.html) as html
  from resume_seat_bullets sb
  join resume_bullets b using (bullet_key)
  join resume_seats s on s.id = sb.seat_id
  join applications a on a.id = s.application_id
 where a.slug = :'slug' and sb.section_id = 'quick-vp'
 order by sb.ord;

-- The comparison he actually wants: the same role across every seat.
select a.slug, sb.ord, coalesce(sb.html_override, b.html) as html
  from resume_seat_bullets sb
  join resume_bullets b using (bullet_key)
  join resume_seats s on s.id = sb.seat_id
  join applications a on a.id = s.application_id
 where sb.section_id = 'quick-vp' order by a.slug, sb.ord;

-- Which bullets a seat re-vectored away from the master, and why.
select a.slug, sb.bullet_key, sb.override_reason
  from resume_seat_bullets sb join resume_seats s on s.id = sb.seat_id
  join applications a on a.id = s.application_id
 where sb.html_override is not null order by a.slug;

-- Master bullets no seat has ever used — dead weight, or an untapped angle.
select b.bullet_key, b.text from resume_bullets b
 where not exists (select 1 from resume_seat_bullets sb where sb.bullet_key = b.bullet_key);

-- Leading-verb collisions across all ten roles. The exact-match half.
select lower(leading_verb) as verb, count(*), array_agg(section_id)
  from resume_bullets where section_kind = 'experience' and retired_at is null
 group by 1 having count(*) > 1;

-- ⚠ The same-root half, which the UNIQUE index CANNOT catch: a leading verb
-- whose stem also appears mid-bullet ANYWHERE, skills block included.
-- This is the `Lifted` / `lifting sales` case from 2026-08-25.
select v.verb, b.section_id, b.text
  from (select distinct lower(leading_verb) as verb from resume_bullets
         where section_kind = 'experience' and leading_verb is not null) v
  join resume_bullets b
    on b.text ~* ('\m' || left(v.verb, greatest(length(v.verb) - 2, 4)))
 where lower(coalesce(b.leading_verb, '')) <> v.verb
 order by v.verb;

-- Hygiene, everything at once. Experience bullets only.
select section_id, ord, word_count, has_bold, has_number, left(text, 60)
  from resume_bullets
 where section_kind = 'experience'
   and (word_count > 25 or not has_bold or not has_number or text ~ '\.$')
 order by section_id, ord;

-- What was actually sent, and whether the file still matches it.
select a.slug, s.state, s.sent_at, s.sent_pdf_path,
       (s.sent_sha256 = encode(sha256(pg_read_binary_file(s.generated_path)), 'hex')) as unchanged
  from resume_seats s join applications a on a.id = s.application_id
 where s.state = 'sent';
```

---

## 9. What makes this harder than it looks

Ranked by how much damage each does if missed.

1. **The section-id contract is silent when broken.** A misspelt id is skipped and the export
   still reports success. Every generator run must assert all ten ids present and non-empty.
2. **Entity spelling is inconsistent in the source, and no formatter fixes it** (§1). Normalise
   once, deliberately, or accept that no diff will ever be clean again.
3. **Three seats are already sent.** Get §5 in before the generator exists, not after — the
   window where a generator can run but the immutability trigger does not is the window in which
   history gets rewritten.
4. **`wolters-kluwer` is `applied` with no PDF at the expected path.** Any migration that assumes
   `<workspace>/Abhisheik_Deo_Resume.pdf` exists for a sent seat will fabricate a path. Record the
   absence.
5. **Same-root verb collisions are not expressible as a constraint** (§4). The `UNIQUE` index will
   make the rule *look* enforced. It is half-enforced.
6. **Two workspaces were being written by other workflows while this was measured** — `modmed`
   and `wolters-kluwer`. Their numbers in §1 are a snapshot. Re-run the proof at cutover.
7. **`master/upgrad_resume.html` is the one résumé file tracked in git**; `**/upgrad_resume.html`
   is gitignored otherwise. So the six workspace files have **no git history to recover from** —
   if a generator corrupts one, the only source is the database. Back up all six before step 7.
8. **The dates in the file are not the dates on the PDF.** The résumé's dates table is an
   assertion; the exported dates live in the Hiration card, which the bot never writes. A
   generated file with correct dates still exports a PDF with whatever the card says. Keep
   verifying the PDF by eye.
9. **The hygiene columns must be derived, never hand-set.** `word_count` that disagrees with
   `text` is the same class of bug as a paste sheet that disagrees with the résumé — a second
   copy of a fact, free to drift.
10. **`resume.py sheet` diffs against git** to decide which sections changed. Once the file is
    generated, "changed since HEAD" answers a different question than it does today. Decide
    whether the sheet should diff the database instead, or keep diffing the artefact.

---

## 10. Current state, for whoever picks this up

**Built and committed (2026-08-26, commit `f07ee1c`), all of it derived and inert:**

- `db/migrations/010_resume_bullets.sql` — creates `resume_bullets`. **Applied** to
  `jobs_tracker_v2`. Idempotent, re-run safe. Its header currently documents the table as
  DERIVED, which is true today and **must be rewritten when the direction flips**.
- `automation/upgrad_resume_paste.py` — `parse_sections()` walks all fifteen sections and
  `role_table()` reads the dates table. Shares `_section_div` and `_block_elements` with the
  exporter's own parser, so the two cannot disagree about what a bullet is. The exporter's
  `parse_resume_paste()` output is **unchanged** — verified.
- `automation/jobs_sync.py --bullets` — the import path. Idempotent, delete-and-reinsert per
  source in one transaction, skips a source that parses to nothing rather than wiping its rows.
- `resume_bullets` holds **488 rows across 7 sources**. **Nothing reads it.** `jobs_db._SELECT`
  is untouched, the launcher is untouched, no test depends on it.

**To remove all of it:** `DROP TABLE resume_bullets;` and revert `f07ee1c`. Nothing else is
affected. **No résumé file was ever written to** — verified by mtime against every one of the
seven files.

**The next action** is step 1 of §7: normalise the master's entity spelling as one small reviewed
commit. Nothing else should start before he has read that diff.
