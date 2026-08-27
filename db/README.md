# `db/` — every piece of SQL in this workspace

Anything that **changes schema or data, or verifies that a change landed**, is a
`.sql` file in here. Ordinary queries stay in the Python that runs them
(`automation/jobs_db.py`, `automation/jobs_sync.py`, `automation/db.py`) — those
are code, not migrations.

```
db/
  README.md          ← you are here
  DESIGN-bullets.md  the forward model: database as source, HTML as view
  schema.sql         the daily log's schema, from scratch
  verify.sql         "is the database in the state I think it is?" — read-only
  migrations/        numbered, applied in order, each one idempotent
    001_reason_to_reasons.sql
    002_empty_reasons_hole.sql
    003_archive_v1_rows.sql      ⛔ applied, then REVERSED — see below
    004_jobs_tracker_v2.sql
    005_move_v2_seats.sql
    006_restore_v1_rows.sql
    007_source_url_nullable.sql
    008_source_note_column.sql
    009_application_events.sql
    010_resume_bullets.sql
    011_resume_versions.sql
    012_resume_master_source.sql
  operations/        re-runnable, once per event, for the rest of the search
    mark_applied.sql
    withdraw.sql
    set_source_url.sql
    log_event.sql
    backfill_status_events.sql   repair — see "when a bare UPDATE gets used"
```

Migrations keep their own subdirectory so the numeric ordering is the first thing
you see. `schema.sql` is deliberately not numbered: it builds `v2_daily` from
nothing, and a fresh run of it already includes everything 001 and 002 added.

**Migrations vs operations.** A migration runs *once* and changes the shape of the
database. An operation runs *every time the thing it describes happens* — a seat is
sent, a seat is withdrawn, a recruiter writes — and changes one row plus its
history. Both are idempotent; only operations are meant to be run again tomorrow.

---

## Three databases

| database | what it holds | who reads it |
|---|---|---|
| **`jobs_tracker`** | **v1's record — 92 seats, frozen.** Every row scraped before 2026-08-25. | Nothing in v2. It is kept, not used. |
| **`jobs_tracker_v2`** | **v2's seats.** Everything from 2026-08-25 onward. | the launcher (`GET /api/jobs`), `jobs_sync.py`, `resume.py new` |
| **`v2_daily`** | the daily log's task state and its append-only event history | `automation/db.py`, `./todo`, `daily/index.html` |

`JOBS_TRACKER_DSN` (default `dbname=jobs_tracker_v2`) selects the first two.
Pointing it at `jobs_tracker` would hand the launcher v1's record, and
`jobs_db.tab_for()` would raise on the first archived row rather than render it.

**Why two job databases and not one with a flag.** He asked for it directly:
*"let's use a different database? like `jobs_tracker_v2`? this way we DO NOT
interfere with v1 jobs?"* A row that has to be filtered out of every single view
is a row in the wrong database. Non-interference is now a property of the
connection string rather than of every query remembering to exclude a status.

---

## Which migration applies to which

| # | database | run it with |
|---|---|---|
| 001 | `v2_daily` | `psql -d v2_daily -f db/migrations/001_reason_to_reasons.sql` |
| 002 | `v2_daily` | `psql -d v2_daily -f db/migrations/002_empty_reasons_hole.sql` |
| 003 | `jobs_tracker` | ⛔ **do not run** — history, reversed by 006 |
| 004 | *creates* `jobs_tracker_v2` | `psql -d postgres -f db/migrations/004_jobs_tracker_v2.sql` |
| 005 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/005_move_v2_seats.sql` |
| 006 | `jobs_tracker` | `psql -d jobs_tracker -f db/migrations/006_restore_v1_rows.sql` |
| 007 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/007_source_url_nullable.sql` |
| 008 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/008_source_note_column.sql` |
| 009 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/009_application_events.sql` |
| 010 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/010_resume_bullets.sql` |
| 011 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/011_resume_versions.sql` |
| 012 | `jobs_tracker_v2` | `psql -d jobs_tracker_v2 -f db/migrations/012_resume_master_source.sql` |

**007–012 all target `jobs_tracker_v2`.** 007 made `source_url` nullable so a seat
with no public listing stores NULL rather than prose; 008 added `source_note` to
hold the reason instead. 009 created `application_events`, the correspondence
timeline. 010 created `resume_bullets`, derived and read-only. 011 added résumé
versioning, whose trigger makes a sent résumé uneditable. **012 flipped the
direction for the master résumé only** — `resume_documents` / `resume_roles` /
`resume_education` / `resume_certifications` / `resume_profile` /
`resume_sections` / `resume_blocks` are AUTHORED, and
`master/upgrad_resume.html` is generated from them by
`automation/resume_db.py`. `resume_bullets` is untouched and stays derived; the
six per-seat workspaces are untouched and stay hand-authored.

---

## Operations — the ones you run again tomorrow

All five take `jobs_tracker_v2`. Every one writes **both** the row and its history;
that pairing is the whole point of the directory.

| operation | when | writes |
|---|---|---|
| `mark_applied.sql` | a seat is sent | `applications.status` + `applied_at` + a `status_events` row |
| `withdraw.sql` | he steps away, with a reason | status + `status_events` + a timeline event |
| `set_source_url.sql` | a posting URL arrives or is cleared | `applications.source_url` |
| `log_event.sql` | anything happens — InMail, reply, document, call | one `application_events` row |
| `backfill_status_events.sql` | repair only | missing `status_events` rows |

```bash
# send
psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 \
     -v slug="'<slug>'" -f db/operations/mark_applied.sql

# record what happened — actor is REQUIRED, detail holds the message VERBATIM
psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
     set_config('ev.slug','<slug>',false), set_config('ev.kind','inbound',false),
     set_config('ev.actor','<who>',false), set_config('ev.summary','<one line>',false),
     set_config('ev.detail','<verbatim>',false)" \
  -f db/operations/log_event.sql
```

⚠ **Quoting.** `log_event.sql` details often contain apostrophes and quotes. Passing
them through `-c` breaks in ways psql reports as a bewildering role-does-not-exist
error. For anything longer than a line, write the `set_config` block to a `.sql`
file with `$ev$…$ev$` dollar-quoting and pass two `-f` flags.

### ⛔ When a bare UPDATE gets used

`backfill_status_events.sql` exists because on 2026-08-26 two seats — Keyloop and
Condé Nast — were moved with

```sql
update applications set status='applied', applied_at=now() where slug in (...);
```

instead of `mark_applied.sql`. The status landed and the history did not, exactly as
`mark_applied.sql`'s own header warns: it writes the `status_events` row "which a
bare UPDATE would forget — and that history is how *when did this go out* survives".
Six seats had the row and two did not, and **nothing in `verify.sql` would ever have
said so.**

The backfill dates each event to the seat's own `applied_at`, never `now()` — a
repair that stamps itself with the moment of repair destroys the one fact it was
written to preserve. Same reasoning as "`updated_at` is never collateral damage".

**The real fix is not that file. It is using the operations.** A status change made
by hand is a status change with no story behind it, which is the v1 failure shape
this directory was built to prevent.

Always add `-v ON_ERROR_STOP=1`, and run from the repo root:

```bash
psql -d postgres -v ON_ERROR_STOP=1 -f db/migrations/004_jobs_tracker_v2.sql
```

Every migration is **idempotent** and ends with a `DO` block that raises rather
than commits if the result is not what it claims. Re-running one is a safe way to
check it is still applied.

Order matters for 004 → 005 → 006: 005 refuses to run if there is nothing to
move, and 006 refuses to delete any seat that `jobs_tracker_v2` cannot confirm it
already holds.

---

## ⛔ 003 is history, not current state

Reading the directory in order will otherwise mislead you.

**003 archived v1's 92 rows in place** on 2026-08-26 — it added an `archived`
value to the `application_status` enum, added `applications.archived_from` under
a CHECK constraint, flipped all 92 rows and logged a `status_events` row for
each. It worked exactly as written.

**006 reversed it the same day**, once he asked for a separate database instead.
`jobs_tracker` today has **no archived rows, no `archived_from` column and no
CHECK constraint**, and its 92 rows carry the statuses v1 left them in.

003 is kept for two reasons: 006 only reads clearly next to it, and the
`archived_from` column 003 invented is precisely what allowed the reversal to
recover the exact distribution rather than guess at it.

**The one thing 006 could not undo:** PostgreSQL has no `DROP VALUE` for an enum.
The `archived` value is still in `jobs_tracker`'s `application_status`, on zero
rows, inert. Removing it would mean recreating the type and every column and
index depending on it, on the one database that must not be rebuilt.
`jobs_tracker_v2` never had it — 004 creates an eleven-value enum and refuses to
commit if `archived` ever appears there.

---

## Verifying

One command, three databases, read-only, safe any time:

```bash
psql -d postgres -v ON_ERROR_STOP=1 -f db/verify.sql
```

It prints what is there and **raises** on anything that must not be. It
distinguishes two things on purpose:

- **Invariants** — must hold for as long as this repo exists. `jobs_tracker`
  frozen at 92 rows with v1's exact distribution; `jobs_tracker_v2` free of any
  archive concept; neither database holding the other's seats; all four original
  v2 seats present by name. These raise.
- **Facts** — supposed to change. How many v2 seats there are, what they scored.
  These print. An assertion on a number `jobs_sync.py` refreshes would fail the
  first time that tool did its job, and a check that cries wolf gets ignored.

Expected output, in short:

```
jobs_tracker      92 rows — recommended_skip 49 · new 15 · resume_finalized 14
                  · applied 10 · resume_drafted 3 · interviewing 1
jobs_tracker_v2   the v2 seats, with their technical scores
v2_daily          task_state and task_event present
```

The four seats 005 moved, and what they scored at the moment of the move:

| slug | technical |
|---|---|
| `yes-madam-lead-architect` | 88.375 |
| `principal-architect-ai-native` | 84.9 |
| `o9-senior-architect-agentic` | 81.4 |
| `wipro-principal-software-architect` | none — no job description to score |

`verify.sql` prints those alongside today's numbers, so drift is visible without
being an error.

The Python suites cover the same ground from the other side:
`bash automation/tests/run.sh`.

---

## Backups

Before the v1/v2 split, `jobs_tracker` was dumped in full to
`~/pg-backup-2026-08-26/jobs_tracker-before-v2-split.sql` (96 rows: v1's 92 plus
the 4 v2 seats, with all `scoring_events` and `status_events`). The earlier
whole-cluster dump is `~/pg-backup-2026-08-25/all-databases-final.sql`. Neither
is in the repo — they hold job descriptions and recruiter notes.

To take a fresh one:

```bash
pg_dump -d jobs_tracker    -f ~/pg-backup-$(date +%F)/jobs_tracker.sql
pg_dump -d jobs_tracker_v2 -f ~/pg-backup-$(date +%F)/jobs_tracker_v2.sql
pg_dump -d v2_daily        -f ~/pg-backup-$(date +%F)/v2_daily.sql
```

---

## Rules that hold across all of it

- **⛔ `applications.salary` is never selected and never rendered.** Compensation
  is deferred by user directive. The column exists because the schema was derived
  verbatim; `automation/tests/test_jobs_db.py` asserts the string `salary` appears
  nowhere in `jobs_db._SELECT` and nowhere in the payload.
- **No SQL lives outside this directory** except the ordinary queries inside
  `jobs_db.py`, `jobs_sync.py` and `db.py`. If a Python script ever needs to run
  a migration, it reads the `.sql` file — the file on disk stays the single
  source of truth, which is the whole reason these are here.
- **`updated_at` is never collateral damage.** Both 003 and 006 disable the
  `BEFORE UPDATE` trigger for their one statement, because stamping every row
  with the moment of a migration destroys "when did this last actually move".

---

## Query it, don't grep it — set by him 2026-08-26

**The database is authoritative for what HAPPENED. The files are authoritative for what is
CLAIMED.** Confusing the two is how the launcher came to show 4 applications while the database
held 92 — markup asserting state — and it is the same failure in reverse if résumé claims move
into tables.

**Query the database for:** status, dates, scores, contacts, the event timeline, counts,
aggregations, invariants, and anything requiring a join. Reading these out of filenames or `ls`
output is strictly worse and silently goes stale.

**Read the files for:** résumé bullet text, the hygiene rules (≤25 words, unique leading verbs, a
bolded fact, acronyms expanded), the honesty checks against `professional-journey.md` and the case
studies, and code. The exporter reads `upgrad_resume.html`; putting bullet text in Postgres would
recreate the drift that merging three files into one removed. CLAUDE.md is explicit: *"Never trust
this list — regenerate it from the file."*

### The queries worth knowing

```sql
-- The board: everything that matters, in one row per seat.
select a.slug, a.status, a.fit_score as tech,
       to_char(a.applied_at,'DD Mon HH24:MI') as sent,
       (select count(*) from application_events e where e.application_id=a.id) as events,
       coalesce(jsonb_array_length(a.hiring_contacts),0) as contacts
  from applications a order by a.applied_at nulls last, a.fit_score desc nulls last;

-- The backlog gate: ready and unsent.
select count(*) from applications where status in ('resume_drafted','resume_finalized');

-- The v1 failure shape: a seat that moved with no story behind it.
select a.slug, a.status, count(e.id) as events
  from applications a left join application_events e on e.application_id=a.id
 group by a.slug, a.status having count(e.id) < 2;

-- One seat's history, in order, with the verbatim text.
select e.occurred_at, e.kind, e.actor, e.summary, e.detail
  from application_events e join applications a on a.id=e.application_id
 where a.slug = :'slug' order by e.occurred_at;

-- Scores in the files that never reached the database (run jobs_sync.py --scores to fix).
select slug, fit_score from applications where fit_score is null;

-- Every seat's source: a URL, a note, or both. Never prose in source_url.
select slug, source_url, source_note from applications order by slug;
```

Full read-only health check across all three databases: `psql -d postgres -f db/verify.sql`.

---

## `resume_bullets` — DERIVED today, and nothing reads it

Migration 010 created `resume_bullets` and `automation/jobs_sync.py --bullets` populates it by
parsing every `upgrad_resume.html`, master included. **488 rows across 7 sources.**

**Today it is a read-only index and the files are still the source of truth.** The exporter reads
`upgrad_resume.html`; nothing reads this table. Editing a row changes nothing about what gets
exported and is overwritten by the next sync. **A wrong bullet is fixed in the résumé, then
re-synced — never in the row.**

```sql
-- What did one seat's VoltusWave bullets say?
select ord, text from resume_bullets
 where source = :'slug' and section_id = 'quick-vp' order by ord;

-- The same role across every seat, side by side.
select source, ord, text from resume_bullets
 where section_id = 'quick-vp' order by source, ord;

-- Which seats still carry a byte-identical copy of the master's résumé.
select distinct source from resume_bullets
 where source_sha256 = (select source_sha256 from resume_bullets where source='master' limit 1);

-- Bullets unique to one seat — nowhere in the master.
select r.source, r.section_id, r.ord, r.text from resume_bullets r
 where r.source <> 'master'
   and not exists (select 1 from resume_bullets m
                    where m.source='master' and m.text = r.text);

-- Leading-verb collisions ACROSS seats, which grep cannot do cleanly.
select lower(leading_verb) as verb, count(distinct source) as seats,
       array_agg(distinct section_id) as sections
  from resume_bullets where section_kind='experience' and leading_verb is not null
 group by 1 having count(distinct section_id) > 1 order by 2 desc;

-- Hygiene misses: over 25 words, or no bolded fact, or no number.
-- Experience only — the summary is prose and the skills block is labels.
select source, section_id, ord, word_count, has_bold, has_number, left(text,60)
  from resume_bullets
 where section_kind='experience'
   and (word_count > 25 or not has_bold or not has_number)
 order by source, section_id, ord;
```

⛔ **`has_number` is a mechanical proxy** — a digit or a `%`. CLAUDE.md's rule is "a number, %,
scale marker, or measurable outcome" and the last two are human judgement. A `false` is worth a
look; a `true` is not a pass, and it is never a reason to add a number.

### Planned: the database as the source

He asked for the direction to flip — bullets authored in the database, `upgrad_resume.html`
generated from it, PDF exported from that. **That is the forward model and it is NOT implemented.**
The design, including a **round-trip proof run against all seven real résumés** (488 bullets,
0 losses, `<strong>` counts preserved exactly), is in **`db/DESIGN-bullets.md`**.

Read that before changing anything here. Two things in it are load-bearing:

- **A rendered artefact is a view — in every format.** HTML page, PDF, `.docx`, plain text. Fixing
  a wrong bullet means fixing the source and regenerating. Never the artefact, never the row.
- **A locally generated PDF does not replace the upGrad/Hiration export.** Hiration produces the
  ATS-scored PDF he submits through upGrad, and `_paste_html` in `upgrad_apply.py` is the only
  path that carries both bold and bullets into the card. Local PDFs and `.docx` files serve the
  *other* need — "email me your CV", portals that want Word, forms that want plain text. **Both
  paths stay. Do not delete the exporter thinking the database replaced it.**
