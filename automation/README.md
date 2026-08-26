# automation/ — Automated upGrad resume build

Drives upGrad's Resume Builder (a Hiration single-page app) via Playwright to
build a tailored resume for one application workspace, export its PDF, and
verify it. Headed by default; set `UPGRAD_HEADLESS=1` to run hidden.

## What the bot does (`upgrad_apply.py`)

Per application, in stages (each is a valid `--stop-after` point):

1. **login** — open careers.upgrad.com; auto-login with the stored encrypted
   creds (falls back to a 5-min manual sign-in poll if creds are missing or a
   captcha / two-factor challenge appears)
2. **nav** — open the resume-builder / "My Resumes" grid
3. **find-master** — locate the `august_master_resume` card
4. **clone** — clone it to `<slug>_ats_resume` (`--reset` deletes a stale clone first)
5. **open-copy** — open the clone in the editor
6. **edit** — overwrite all **10 sections** from the workspace's
   `upgrad_resume.html` (headline, summary, the 3 skills sub-lists, and the 5
   experience roles)
7. **score** — read the Hiration Resume Review score (0–100)
8. **export** — save the PDF to `<workspace>/Abhisheik_Deo_Resume.pdf`
9. **verify** — check every expected text fragment is present in the PDF
10. **summary** — print JSON + write `<workspace>/_upgrad_run.json`

The script writes **no HTML and no database**. **Dates live in the Hiration
card, not the HTML** — the bot overwrites bullet TEXT but not role dates, so the
master card must already carry the correct VP end date (Apr 2026). Status pills
in the workspace `index.html` and the in-flight memory are updated separately.

The temp `<slug>_ats_resume` clones pile up in the Hiration account — delete
them after each run (or a batch) with **`cleanup_cards.py`** (below).

## One-time setup

```bash
python3 -m venv automation/.venv
automation/.venv/bin/pip install -r automation/requirements.txt
automation/.venv/bin/playwright install chromium
```

## Credentials (encrypted, git-ignored)

Login is automated. Store the upGrad username/password once — encrypted at rest
with a local Fernet key. Both `.upgrad_key` and `.upgrad_creds.enc` are
git-ignored and `chmod 600`, and are **NEVER committed** (the password is read
from STDIN so it never lands in argv / shell history):

```bash
printf '%s\n%s\n' "user@example.com" 'the-password' \
  | automation/.venv/bin/python automation/upgrad_creds.py set
automation/.venv/bin/python automation/upgrad_creds.py check   # prints username only
```

With creds stored, the bot signs in on its own. Without them — or if a
captcha / two-factor challenge appears — it falls back to a manual sign-in you
complete in the Chromium window. To seed or refresh the persistent session
(`.playwright-profile/`) by hand:

```bash
automation/.venv/bin/python automation/login.py upgrad
```

It auto-exits once you're past the login form (5-min timeout).

## Run

```bash
automation/.venv/bin/python automation/upgrad_apply.py --slug <workspace-slug>

# typical headless batch run (fresh clone, no stage pauses):
UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py \
  --slug <workspace-slug> --no-pause --reset
```

`<workspace-slug>` is the workspace directory name, resolved across the
root-level `<slug>/`, dated `<Month-YYYY>/<DD>/<slug>/`, and legacy
`<DD-MM-YYYY>/<slug>/` / `<DD-Month-YYYY>/<slug>/` layouts. The workspace must
contain a complete `upgrad_resume.html` (the 10-section contract above; see
CLAUDE.md → "Automated upGrad export").

### Flags

| Flag | Purpose |
|------|---------|
| `--slug <slug>` | **Required.** Workspace to build the resume for. |
| `--stop-after <stage>` | Stop after a stage (inclusive). Stages: `login nav find-master clone open-copy edit score export verify summary`. Default `summary`. |
| `--output <path>` | PDF output path override (default `<workspace>/Abhisheik_Deo_Resume.pdf`). Use a temp path while testing so you don't clobber a committed PDF. |
| `--master <title>` | Master resume card title (default `august_master_resume`; env `UPGRAD_MASTER_CARD` overrides the default). |
| `--bullets-as-paragraphs` | Paste experience bullets as `<p>` instead of `<ul><li>` — bold-survival fallback (see below). |
| `--no-pause` | Don't pause between stages. |
| `--reset` | Delete an existing `<slug>_ats_resume` in upGrad first (start fresh). |
| `--slow <ms>` | Playwright `slow_mo` for debugging. |

### Environment

| Var | Effect |
|-----|--------|
| `UPGRAD_HEADLESS=1` | Run Chromium hidden (default is **headed** — Hiration may fingerprint-detect headless, so headed is the safe fallback if a run gets blocked or captcha'd). |
| `UPGRAD_MASTER_CARD` | Override the master card title (same as `--master`). |

On any stage failure the page is dumped to `.debug/upgrad/error-<stage>.{html,png}`.

## Clean up the temp clones (`cleanup_cards.py`)

Deletes every card whose name ends in `_ats_resume` — the per-run clones the bot
creates. The protected set is `june_master_resume`, `august_master_resume` and
`master_ic_architect`; any card without the `_ats_resume` suffix is protected and
never touched. The exported PDFs already live in each workspace, so deleting the
cards loses nothing.

```bash
automation/.venv/bin/python automation/cleanup_cards.py            # delete them
automation/.venv/bin/python automation/cleanup_cards.py --dry-run  # list only
```

## Bold-in-lists caveat (must check)

upGrad's **manual** paste strips `<strong>` inside `<ul>/<li>` but keeps it in
paragraphs (this is why `bullets_for_upgrad.html` exists). The automation's
synthetic paste goes into Draft.js's importer, which **may** preserve list
`<strong>` — unverified. After a run, **open the PDF and confirm
experience-bullet bold renders heavier** (the verify stage only checks that text
is present, not that bold survived). If bold is flat, re-run with
`--bullets-as-paragraphs` (loses the bullet glyph, preserves bold).

## The launcher reads PostgreSQL (`jobs_db.py` · `jobs_sync.py`)

The workspace launcher (`index.html`) used to carry its application cards as
hand-written markup, appended by `resume.py new`. That is why the page once
showed **four** rows while the database held **ninety-two**. The database is the
search layer; directories are storage, not an index — so the page renders from
the database instead.

⚠ **It reads `jobs_tracker_v2`, not `jobs_tracker`.** v2 has had its own database
since 2026-08-26. v1's ninety-two rows are in `jobs_tracker` and nothing here
opens it. See **`db/README.md`** for the three databases, the migrations and
`db/verify.sql`.

```
automation/.venv/bin/python automation/serve.py       # GET /api/jobs
automation/.venv/bin/python automation/jobs_db.py     # per-tab counts, on the CLI
automation/.venv/bin/python automation/jobs_sync.py   # seed + refresh scores
automation/.venv/bin/python automation/jobs_sync.py --scores --dry-run
```

- **`jobs_db.py`** — read-only queries against `jobs_tracker_v2`
  (`JOBS_TRACKER_DSN`, default `dbname=jobs_tracker_v2`). Sibling of `db.py`,
  which owns `v2_daily`; the two never share a connection. Nothing here writes,
  so the module `serve.py` imports cannot mutate the record.
- **`jobs_sync.py`** — the write side, deliberately in its own file. `seed`
  registers the seats that existed only as directories (ON CONFLICT DO NOTHING,
  so a re-run never overwrites a status changed since); `scores` re-reads every
  workspace's `score.json` and refreshes `fit_score` / `fit_breakdown` from its
  `weighted_total`. **Scores are never hardcoded** — three of the four moved on
  2026-08-25 alone — so re-run this whenever a rubric is re-adjudicated.
- **`serve.py`** — `GET /api/jobs` returns `{store, counts, applications}`.
  Same error handling as the daily endpoints: **503 when the database is
  unreachable**, and the launcher then says the list is unavailable rather than
  rendering an empty grid, which would read as "no applications".
- **`static/apps.js`** renders the rows; **`static/tabs.js`** keeps the tab
  contract (tab buttons carry `data-tab`, rows carry `data-status`) and owns the
  search box, so tab and search compose instead of fighting over `hidden`.
  **Counts are derived from the rows in the DOM, never passed in**, and a
  `MutationObserver` on `#app-list` re-derives them whenever it changes — the
  rows arrive asynchronously, and a count computed before the fetch resolves
  read 0 above a full list. `initTabs()` still exists and still works; nothing
  depends on it being called.
- **`resume.py new`** registers the seat in `jobs_tracker_v2` as `resume_drafted`,
  which shows under **Ready to apply**. It no longer writes markup into
  `index.html`. **Never hand-write a row there** — a row added by hand is a row
  no query can see.
- **`automation/intake_notes.json`** — hand-authored clauses for the intake-date
  group headers, keyed by ISO date. **Ships empty and stays empty until he
  writes one.** The date and the seat count are derived; the sentence about what
  a group of seats *was* is not derivable and is never composed.

⛔ `applications.salary` is never selected, returned or rendered. Compensation
is deferred by user directive.

### Status → launcher tab

Eleven `application_status` values, six tabs — v1's tab set exactly. Every row
lands in exactly one tab; `tab_for()` raises `UnknownStatus` on anything unmapped
rather than dropping a row, and `counts()` asserts the tabs total the row count.

**There is deliberately no `all` tab**, exactly as in v1. `ready` is the tab that
opens.

⚠ **There is no `archived` tab either, and no archive concept at all.** There was
one, for a day: `db/migrations/003` archived v1's 92 rows in place and gave them
a seventh tab. `db/migrations/006` reversed it once he asked for a separate
database instead. `archived` is not in `TAB_FOR_STATUS`, not in `TABS`, and not
even in `jobs_tracker_v2`'s enum — PostgreSQL refuses such a row before this
module is asked for its tab.

| tab | statuses | why |
|---|---|---|
| **Ready to apply** | `recommended_apply` · `resume_drafted` · `resume_finalized` | The apply queue: decided to pursue, not yet sent. v1's tab was this broad (its stage map put jd-saved, changes-drafted and resume-finalized all in `ready`) and its count is the backlog gate — *"23 rows sitting in the ready tab, unsent"*. |
| **Applied** | `applied` | It went out; nothing back yet. |
| **No longer available** | `withdrawn` | He pulled out, or the seat went away. Terminal, and deliberately **not** a rejection — v1's record is explicit that conflating the two loses the only thing the row still says. |
| **Heard back** | `heard_back` · `interviewing` · `offer` | They replied and the process is live. This tab set has no interviewing tab, and burying a live process in `other` would be the worst answer available. |
| **Not selected** | `rejected` | |
| **Other** | `new` · `recommended_skip` | The catch-all, which is what a catch-all is for. It also retires the judgement call v2 inherited: 49 `recommended_skip` rows were scored and adjudicated out before any build, and they belong neither in the apply queue (they would corrupt the backlog gate) nor among seats that closed on their own. |

### v1 and v2 are separate databases — `db/migrations/004`, `005`, `006`

Set by him on 2026-08-26: *"let's use a different database? like
`jobs_tracker_v2`? this way we DO NOT interfere with v1 jobs?"*

| database | holds | read by |
|---|---|---|
| `jobs_tracker` | v1's record — **92 seats, frozen**, everything scraped before 2026-08-25 | nothing in v2 |
| `jobs_tracker_v2` | v2's seats, everything from 2026-08-25 onward | the launcher, `jobs_sync.py`, `resume.py new` |

- **004** creates `jobs_tracker_v2` with `jobs_tracker`'s schema, derived from
  `pg_dump --schema-only` so it cannot drift, minus exactly the three things 003
  added: the `archived` enum value, `applications.archived_from`, and the CHECK
  constraint.
- **005** moves the four v2 seats across with `scoring_events`, `status_events`
  and their ids, then compares every field back across the connection before it
  commits.
- **006** reverses 003 and deletes those four from `jobs_tracker`, but only the
  ones `jobs_tracker_v2` confirms it already holds. `jobs_tracker` ends at 92
  rows with v1's exact distribution: `recommended_skip` 49 · `new` 15 ·
  `resume_finalized` 14 · `applied` 10 · `resume_drafted` 3 · `interviewing` 1.

**⛔ 003 is history, not current state.** It archived the 92 rows in place and was
reversed the same day. Do not re-run it. The `archived_from` column it invented is
what let 006 recover the exact distribution rather than guess at it — which is why
both files are kept.

**The one thing 006 could not undo:** PostgreSQL has no `DROP VALUE` for an enum,
so `archived` is still in `jobs_tracker`'s `application_status`, on zero rows,
inert. `jobs_tracker_v2` never had it.

**`updated_at` was preserved through both.** The BEFORE UPDATE trigger is disabled
for the one statement in each, because stamping all 92 rows with the moment of a
migration destroys "when did v1 last touch this".

Verify any of it, read-only, any time:

```
psql -d postgres -v ON_ERROR_STOP=1 -f db/verify.sql
```

Full detail, including how to run each migration: **`db/README.md`**.

### The two scores

`applications` predates CLAUDE.md's two-score model and carries one composite
`fit_score`, so both numbers are read out of `fit_breakdown`:

- **v2 seats** — `jobs_sync.py` writes `{"rubric": "v2-weighted", "technical": N}`
  straight from the workspace's `score.json` `weighted_total`. No non-technical
  number is computed in v2, so it renders `—`. Nothing is invented to fill it.
- **v1 seats** — the five-axis breakdown splits along the same line, so this is
  a rescale of v1's own axes, not a new judgement:
  `technical = hard_reqs / 40`, `non-technical = (level + domain + location +
  freshness) / 55`, both to `/100`.

**The two are not comparable** — different rubrics — which is why every row also
carries `rubric`, and why **the launcher does not print a v1 row's numbers in the
score columns at all**: they read `v1` instead. "technical 20" beside
"technical 88.4" invites a ranking that does not exist. The rescaled figures are
still computed, still served, and shown in the row's expanded detail where they
can be labelled.

## Other scripts in this directory

- **`html_to_pdf.py`** — standalone renderer, unrelated to upGrad: turns any
  local HTML file(s) into a sibling `<name>.pdf` via headless Chromium, faithful
  to CSS/bold (unlike a browser "Print to PDF"). `automation/.venv/bin/python
  automation/html_to_pdf.py <file.html> [<file2.html> ...]`.
- **`browser.py`** — shared Playwright context helper (persistent
  `.playwright-profile/`, honors `UPGRAD_HEADLESS`); imported by the others.
- **`login.py`** — seed/refresh the login session (above).
- **`upgrad_creds.py`** — the encrypted credential store + auto-login (above).
- **`job-capture-extension/`** — an unbuilt Chrome-extension **plan**
  (`PLAN.md`), not part of this bot.

## Prerequisites / notes

- The `august_master_resume` card must exist in the Hiration account with the 5
  roles in order — vp, deque, rocket, voltuswave-cofounder, teletext — because
  the editor binds them positionally to `#PR-child-0..4`.
- First runs are easiest **headed** (a Chromium window opens) so you can watch
  the auto-login and hand off if a challenge appears.
- The automation finalizes the resume PDF only — it does **not** submit to any
  company.
