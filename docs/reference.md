# Reference — how-to details for this repo

Moved out of `CLAUDE.md` on 2026-09-28 so the rulebook stays short. `CLAUDE.md` holds the rules;
this file holds the how. Full history: `docs/CLAUDE-original-2026-09-28.md`.

## Commands
- **Server:** `automation/.venv/bin/python automation/serve.py` — port 8006, bound to 127.0.0.1,
  sends no-store, provides the state API. Never `python3 -m http.server` (under it the launcher says
  the list is unavailable).
- **Scaffold a seat:** `automation/.venv/bin/python automation/resume.py new --slug <slug> --url <url> [--company X --role Y]`.
  It refuses without `--url <url>` or `--no-url "<reason>"`.
- **Per-seat résumé:** the master is `master/Abhisheik_Deo_Resume.docx`. A per-seat résumé is a
  selection with edits in `resume_versions` / `resume_version_bullets`.
  `automation/.venv/bin/python automation/resume_docx.py generate [--slug <slug>]`, then
  `verify_resume_docx.py <file> --doc-key seat:<slug>` (without `--doc-key` it passes falsely).
  `resume_docx.py` refuses rather than emit a wrong document. Its bold gate counts occurrences, not
  membership. Never set `run.bold = False`. Migration 011's trigger stops edits to a sent version.
- **The board:**
  `psql -d jobs_tracker_v2 -c "select slug, company, status, fit_score, applied_at from applications order by fit_score desc nulls last;"`
- **Verb pool** (`orchestrat` and `Built` are taken):
  ```sql
  -- every leading verb in use, across all ten roles
  psql -d jobs_tracker_v2 -At -c "select b.leading_verb from resume_blocks b join resume_sections s on s.doc_key=b.doc_key and s.section_id=b.section_id where b.doc_key='master' and s.section_kind='experience' and b.retired_at is null and b.leading_verb is not null order by 1;"
  -- is a stem free? same-root collisions hide mid-bullet, so search the whole document
  psql -d jobs_tracker_v2 -At -c "select section_id, ord, substring(text,1,70) from resume_blocks where doc_key='master' and retired_at is null and text ~* '<stem>';"
  ```
- **Timeline event** (`application_events`: `actor` required — the named person, or "Abhisheik";
  `detail` verbatim; `artefact` = the repo path when a file changed hands; append-only — correct by
  adding an event):
  ```
  psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('ev.slug','<slug>',false), set_config('ev.kind','inbound',false), set_config('ev.actor','<who>',false), set_config('ev.summary','<one line>',false), set_config('ev.detail','<verbatim>',false)" -f db/operations/log_event.sql
  ```
- **Operations** in `db/operations/`: `mark_applied.sql` (its usage comment is wrong — pass
  `set_config('mark_applied.slug',…)`), `set_status.sql`, `withdraw.sql`, `set_source_url.sql`,
  `log_event.sql`, `clone_seat_resume.sql`. For text containing quotes, put the `set_config` select
  in a scratch `.sql` file (dollar-quoted) and run `psql -f that.sql -f db/operations/<op>.sql`.
- **Tests:** `bash automation/tests/run.sh`.

## Database and launcher
- **All SQL lives in `db/` and is re-runnable.**
- The launcher (`index.html`) renders from `jobs_tracker_v2` via `/api/jobs`; never hand-write rows.
  Six tabs over eleven statuses, no `all` tab, **no archive concept** (never re-run migration 003).
  v1-rubric rows show `v1`, not a number. Group headers are `<date> — N seats` only. Counts derive
  from the rendered rows. `applications.salary` is never selected or rendered.
- `jobs_tracker` (v1, 92 seats) is frozen and never opened; `jobs_tracker_v2` is v2. Verify both
  read-only: `psql -d postgres -f db/verify.sql`. `automation/jobs_db.py` is read-only;
  `automation/jobs_sync.py` registers a seat and refreshes scores from `score.json` (idempotent;
  never overwrites a five-axis breakdown).
- **Round-trip gate** for loading résumé content: load → regenerate → diff, byte-identical or every
  difference justified. A lossy parse is the worst outcome: stop rather than proceed, and never
  leave a migration half-done. `master/upgrad_resume.html` is generated for this check only.
- **Daily log:** `daily/index.html` is generated from `daily/days.json` by `automation/daily.py`;
  state lives in PostgreSQL `v2_daily`. `./todo` coordinates and never executes. Moving a task out
  needs a reason (revivable only if every reason is revivable); unfinished tasks roll over; never
  duplicate one.

## Automation scripts and retired paths
- `automation/upgrad_resume_paste.py` is the shared résumé parser — load-bearing, never "clean it up".
- `automation/cleanup_cards.py` never runs unless he names a card.
- **upGrad / Hiration is retired** (access revoked 27 Aug 2026); every entry point exits 3 on
  purpose, so never diagnose that as a bug. History: `docs/RETIRED-upgrad-pipeline.md`. Keep
  `master/live_card_dump*` (the only record of the cards). Never send
  `master/Abhisheik_Deo_Resume.SUPERSEDED-2026-08-25.pdf`.

## Pages, paths and wording
- No per-file `<style>`; shared classes live in `style.css` (`.page.full` is full width).
- Breadcrumbs: the month crumb opens the launcher with `?month=YYYY-MM`, the day crumb with
  `?date=YYYY-MM-DD`. `static/apps.js` passes these to `/api/jobs`, which filters in SQL
  (`jobs_db.applications(month, day)`; 400 if malformed), so groups, tabs and counts are that
  month's or day's. The slug crumb uses `?q=` (text search in the browser). `static/tabs.js` opens
  the first tab with a match.
- Copy buttons: `data-copy-target="#id" data-copy-html="1"` (keeps bold).
- Workspaces are `Month-YYYY/DD/<slug>/`, three levels below the repo root; raw inputs go in
  `job-applications/Month-YYYY/DD/`. Open, his call: a flat `<repo>/<slug>/` layout instead.
- Naukri's job-profile box rejects `<` and `\`: write "under", "within", "at X+".
- Case-study wording: write "tenant-scoped traversal-source wrapper", not `TraversalSource`. Status
  vocabulary, never upgraded: shipped-production · shipped-ci-only · designed-reviewed ·
  designed-only · unclear. v2 lands in `killer-query-case-studies-v2/` (never overwriting v1): diff it
  against v1 and carry every downgrade.
- Company facts belong in each seat's `research.html`. `/last30days` found nothing on these
  employers in August 2026, so never claim social buzz.

## Agents outside a job
- At most 5 per workflow and per turn. Never nest `parallel()` inside `pipeline()`; slice fan-outs
  and log what was dropped. Ultracode is no licence to skip proportion.

## Measurement traps
- Word counts ignore punctuation tokens: count only tokens containing a letter or digit.
- `grep -c` counts lines, not occurrences, and these files are minified.
- The LinkedIn URL sits in a PDF link annotation, not the text.
- A missing script throws nothing, so prove features work.
- Regex context windows give false positives: search case-sensitive, word-bounded and tag-stripped.
- Enumerate every source before concluding about "the" source.
- The local `grep` (ugrep) rejects long context patterns; use Python.
