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
hand-written markup, appended by `resume.py new`. That is why the page showed
**four** rows while `jobs_tracker` held **ninety-two**. The database is the
search layer; directories are storage, not an index — so the page renders from
the database instead.

```
automation/.venv/bin/python automation/serve.py       # GET /api/jobs
automation/.venv/bin/python automation/jobs_db.py     # per-tab counts, on the CLI
automation/.venv/bin/python automation/jobs_sync.py   # seed + refresh scores
automation/.venv/bin/python automation/jobs_sync.py --scores --dry-run
```

- **`jobs_db.py`** — read-only queries against `jobs_tracker`
  (`JOBS_TRACKER_DSN`, default `dbname=jobs_tracker`). Sibling of `db.py`, which
  owns `v2_daily`; the two never share a connection. Nothing here writes, so the
  module `serve.py` imports cannot mutate v1's record.
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
  contract (pills carry `data-tab`, rows carry `data-status`) and now also owns
  the search box, so tab and search compose instead of fighting over `hidden`.
- **`resume.py new`** registers the seat in `jobs_tracker` as `resume_drafted`.
  It no longer writes markup into `index.html`. **Never hand-write a card
  there** — a row added by hand is a row no query can see.

⛔ `applications.salary` is never selected, returned or rendered. Compensation
is deferred by user directive.

### Status → launcher tab

Eleven `application_status` values, nine tabs. Every row lands in exactly one
tab; `tab_for()` raises `UnknownStatus` on anything unmapped rather than
dropping a row, and `counts()` asserts the tabs total the row count.

| status | tab | why |
|---|---|---|
| `new` | **parked** | Scraped, never triaged: no score, no decision, no workspace. Not `building` (nothing is being built), not `closed` (nothing was decided). `parked` is "set aside, can come back". |
| `recommended_apply` | **building** | The decision to pursue is made; the workspace is the next step. |
| `recommended_skip` | **closed** | **The deliberate one — 49 rows.** Scored and adjudicated out before any build, each with its `rec_reasoning`. In `parked` they would bury the few builds he actually paused; in `building`/`ready` they would corrupt the ready-and-unsent count, which is the backlog gate v2 is organised around. `closed` is the archive: decided, not pursued. |
| `resume_drafted` | **building** | Workspace under way. |
| `resume_finalized` | **ready** | Exported and unsent — the backlog gate. |
| `applied` | **sent** | |
| `heard_back` | **responded** | |
| `interviewing` | **interviewing** | |
| `offer` | **interviewing** | There is no offer tab. An offer is the furthest-along *live* process, so it sits with the other live one rather than in `responded`, which reads as "they replied". |
| `rejected` | **not-selected** | |
| `withdrawn` | **closed** | He pulled out. Terminal, and deliberately not a rejection. |

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
carries `rubric` and the page says so under the search box.

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
