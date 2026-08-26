# `db/` — every piece of SQL in this workspace

Anything that **changes schema or data, or verifies that a change landed**, is a
`.sql` file in here. Ordinary queries stay in the Python that runs them
(`automation/jobs_db.py`, `automation/jobs_sync.py`, `automation/db.py`) — those
are code, not migrations.

```
db/
  README.md          ← you are here
  schema.sql         the daily log's schema, from scratch
  verify.sql         "is the database in the state I think it is?" — read-only
  migrations/        numbered, applied in order, each one idempotent
    001_reason_to_reasons.sql
    002_empty_reasons_hole.sql
    003_archive_v1_rows.sql      ⛔ applied, then REVERSED — see below
    004_jobs_tracker_v2.sql
    005_move_v2_seats.sql
    006_restore_v1_rows.sql
```

Migrations keep their own subdirectory so the numeric ordering is the first thing
you see. `schema.sql` is deliberately not numbered: it builds `v2_daily` from
nothing, and a fresh run of it already includes everything 001 and 002 added.

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
