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
3. **find-master** — locate the `june_master_resume` card
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
| `--master <title>` | Master resume card title (default `june_master_resume`; env `UPGRAD_MASTER_CARD` overrides the default). |
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
creates. `june_master_resume` and any card without that suffix are protected and
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

- The `june_master_resume` card must exist in the Hiration account with the 5
  roles in order — vp, deque, rocket, voltuswave-cofounder, teletext — because
  the editor binds them positionally to `#PR-child-0..4`.
- First runs are easiest **headed** (a Chromium window opens) so you can watch
  the auto-login and hand off if a challenge appears.
- The automation finalizes the resume PDF only — it does **not** submit to any
  company.
