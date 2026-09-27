# CLAUDE.md — Full-time JD workspace (v2)

Succinct rulebook, written for Claude. The full version — history, incidents, his exact words — is
`docs/CLAUDE-original-2026-09-28.md`; read it when the reason behind a rule matters.
**Read `RESUME_SESSION.md` first, every session.**

## Purpose
- Tailored résumés and research for **individual-contributor (IC) seats only**: Principal, Staff,
  Architect, Solution Architect, Senior Engineer. Never source a leadership seat (Director, VP, Head,
  Engineering Manager) or rank one into the apply-first queue. But every JD he pastes gets the full
  build without re-asking; the only open question is whether to *send* it.
- **Sending is the goal, not building.** A build is done when it is sent, or parked with a written
  reason. When ready-and-unsent passes about five, say so; that steers attention and never blocks a build.
- **A full workspace:** `jd.md` / `jd.html` (+ card screenshots) · weighted-rubric `index.html` ·
  `resume_changes_for_<N>pct_match.html` · cited `research.html` (verdict, red and green flags,
  forcing questions, never compensation) · `score.json` · the generated and verified per-seat
  `.docx`. Every workspace needs an `index.html`; the launcher links the directory.
- v1 is abandoned. Nothing outside this directory is in scope.

## Source of truth
- `professional-journey.md` is the truth; the master résumé is derived from it and loses on any
  conflict. It still carries v1's `OPEN →` markers. His additions to it are first-class intake:
  reconcile them against what is claimed and flag contradictions, never smooth them over.
- Before restructuring anything he wrote by hand, copy it verbatim to `<name>-original.md` and point
  to it. Check `git status` first.
- **The database (`jobs_tracker_v2`) is the source** of résumé content: bullets, skills, headline,
  summary, roles, education, certifications, personal details. HTML is a view.
  `master/upgrad_resume.html` is generated for the round-trip check only, never hand-edited.
  **Query the database; never grep résumé files.**
- Round-trip gate: load → regenerate → diff, byte-identical or every difference justified. A lossy
  parse is the worst outcome: stop rather than proceed, and never leave a migration half-done.
- He supplies material, not markup. Agents draft and stage; nothing ships on his behalf.
- His confirmations (Aug 2026): Kubernetes, Terraform, HIPAA, load balancing, high availability. The
  interview-prep honesty ledger disagrees on Kubernetes — open, his call.

## Per-seat résumé (his rules, 24 Sep 2026)
- Start from the master (`master/Abhisheik_Deo_Resume.docx`) and aim for a 95+% match to the JD.
- Put the edits only in the last five roles: VoltusWave (Principal Software Architect), Deque
  Software, Rocket Software, VoltusWave (Co-Founder & VP of Technology), Teletext India.
- `resume_changes_for_<N>pct_match.html` gives one copy block per organisation, to verify and paste.
- A per-seat résumé is a selection with edits in `resume_versions` / `resume_version_bullets`, never
  a copied file. Output is `.docx`, which he edits in Word:
  `automation/.venv/bin/python automation/resume_docx.py generate [--slug <slug>]`, then
  `verify_resume_docx.py <file> --doc-key seat:<slug>` (without `--doc-key` it passes falsely).
- `resume_docx.py` refuses rather than emit a wrong document. Its bold gate counts occurrences, not
  membership. Never set `run.bold = False`.
- **New jobs only.** Every seat past a pre-send state is frozen: no `.docx`, regeneration or edits
  (migration 011's trigger enforces it). The sent PDFs are the record.

## Résumé hygiene — every bullet
- At most 25 words (count only tokens containing a letter or digit) · a strong verb opener, never
  Managed / Replaced / Responsible for / Worked on / Helped · a leading verb unique across the
  résumé, where same-root variants collide · at least one number, percentage, scale marker or
  outcome · at least one bolded fact · no trailing period · every acronym expanded on first use (the
  headline may keep common ones; the summary expands them). Reference: `resume-issues-to-avoid/`.
- Expand acronyms and unfamiliar terms on first use **everywhere**: pages, dashboards, chat. For an
  unfamiliar domain, put a plain-English glossary at the top of `research.html` that defines the
  concept. Call out collisions (SOC 2 the audit vs a SOC; RAG = Red/Amber/Green status vs
  retrieval-augmented generation).
- The verb pool is a query, never a list kept here (`orchestrat` and `Built` are taken):
  ```sql
  -- every leading verb in use, across all ten roles
  psql -d jobs_tracker_v2 -At -c "select b.leading_verb from resume_blocks b join resume_sections s on s.doc_key=b.doc_key and s.section_id=b.section_id where b.doc_key='master' and s.section_kind='experience' and b.retired_at is null and b.leading_verb is not null order by 1;"
  -- is a stem free? same-root collisions hide mid-bullet, so search the whole document
  psql -d jobs_tracker_v2 -At -c "select section_id, ord, substring(text,1,70) from resume_blocks where doc_key='master' and retired_at is null and text ~* '<stem>';"
  ```
- **Rule 7 — re-vector per job, always.** Back each surfaced skill with bullet evidence across the
  current role and 2–3 prior. Edit in place, keeping the leading verb; add a bullet only with a verb
  confirmed free. Real work only.

## Scoring
- **Technical score, target 95+.** This is the one he cares about. A weighted rubric (criterion,
  weight, score out of ten, evidence). Read "e.g. / or / preferably" generously. A named tool he has
  not used is a ramp item, not a cap; only a genuinely core missing technology caps the score. Name
  the binding constraint and the smallest honest lift, usually Rule 7. Never fabricate to reach 95:
  an honest 88 beats an invented 95.
- **Non-technical score:** informational only, never a gate, never a drag.
- Real-world gates (levelling, legitimacy) are named separately from both scores. Apply broadly;
  honesty governs résumé content, never whether to apply.

## Compensation — deferred
- Do not research, surface, gate on, flag or score it until a company responds and the conversation
  reaches that stage. A band in a JD goes into `jd.md` as a neutral fact, nothing more.
  `applications.salary` is never selected or rendered.
- When it is asked: expected **₹75L–₹1Cr fixed** (midpoint ₹87.5L), anchored to the seat's level.
  Current CTC **₹72L** is never volunteered or put in a draft unprompted. When he says disclose it,
  disclose: name the trade once (it anchors the band near ₹72–75L), then proceed.

## Voice and replies
- Drafted prose reads human: no aphoristic closers, no "three loops", light on em dashes, never
  "non-negotiable", "blast radius" or "compounds over a career".
- Outward-facing pieces lead with strengths and never volunteer gaps; internal pages name gaps plainly.
- Anything he will paste is staged as HTML with a working copy button
  (`data-copy-target="#id" data-copy-html="1"`), never as chat text.
- **Recruiter replies:** answer exactly what was asked, in order; add no questions of your own; lead
  with *available immediately, nothing to serve*; include **+91 93640 27487** when inviting a call;
  offer a slot about 2 days out, never tomorrow. Everything else goes to the call cheat-sheet.
- Naukri's job-profile box rejects `<` and `\`: write "under", "within", "at X+".

## Intake
- He pastes; we build. **Always ask for the posting URL.** `resume.py new` refuses without
  `--url <url>` or `--no-url "<reason>"`. `source_url` is a URL or NULL, never prose (the launcher
  renders it as a link). Raw inputs go in `job-applications/Month-YYYY/DD/`.
- Never source seats. Never re-rank or recommend an order unless asked; report audit results as findings.
- Open, his call: a flat `<repo>/<slug>/` layout versus the current `Month-YYYY/DD/<slug>/`.

## Agents — MAX 3 PER JOB (his rule, 28 Sep 2026)
- **No job gets more than 3 agents in total,** across every turn and phase, including its interview
  prep. Count per job, not per turn. If a job needs more, ask first. (Delta, 27 Sep: 15 agents where
  about 5 would have done.)
- The standard split: **(1)** research and JD pages (`jd.md`, `jd.html`, cited `research.html`) ·
  **(2)** scoring and résumé edits (`score.json`, proposed edits; after adjudication, resume the same
  agent with SendMessage for the rubric `index.html` and the `resume_changes` page) · **(3)** one
  adversarial check of every proposed claim.
- One agent covers every research angle, every rubric criterion, every résumé section. Batch small
  edits into one pass. Size the output so one checker can verify it.
- Outside a job (tooling, audits): at most 5 per workflow and per turn. Never nest `parallel()` inside
  `pipeline()`; slice fan-outs and log what was dropped. Deterministic checks are scripts, never
  agents. Ultracode is no licence to skip proportion.
- **Why delegate at all: keep this CLI answerable.** Content landing in a workspace is delegated —
  "it's only mechanical" is no exemption. Launch in the background, keep talking, never poll.
- **Main thread only:** adjudication, the adversarial verify pass against `professional-journey.md`,
  his decisions, coordination, conversation, and running commands that already exist.
- **Verification is not optional.** Agents get about 1 claim in 10 wrong. Unsupported claims are cut,
  not softened, and the checker is adjudicated too.
- **Never resolve the open claims** — the graph neural network, the four Rocket metrics, the 70–80%
  consolidation, the 27 ms / P95 16 ms pairing, the 100,000-concurrent wording. Surface them; leave
  the résumé wording alone.
- Report results in two to four plain lines: done, needs his decision, still running. Tell him the
  rough time a build will take before starting it.

## Honesty landmines — `killer-query-case-studies/`
- v1: ten case studies on Amura, a chronic-care platform (80+ conditions). All of v1 **shipped**;
  "approval pending" means a design-review sign-off, not deployment status.
- **He has no outcome numbers** — he left VoltusWave before capturing them. Never invent one, never
  ask again. Safe markers only: 80+ conditions, a 6-hour cache TTL (KQ4; KQ1's is 1 hour), a 90-day
  outcome-maturity window, twenty review findings absorbed into a hardened v2, 13 of 13 local
  findings closed, 9–10 years of patient history.
- **KQ2's served-cell table is illustrative:** 412, 217, 0.58, 0.34, +24pp and 0.08 never appear as
  outcomes. Nor does KQ1's "300 patients".
- Amura names no message broker; Kinesis belongs to the chat platform only.
- Write "tenant-scoped traversal-source wrapper", not `TraversalSource`.
- Status vocabulary, never upgraded: shipped-production · shipped-ci-only · designed-reviewed ·
  designed-only · unclear.
- Don't wait for v2. When it lands in `killer-query-case-studies-v2/` (never overwriting v1), diff
  it against v1 and carry every downgrade.

## Database and automation
- The launcher (`index.html`) renders from `jobs_tracker_v2` via `/api/jobs`; never hand-write rows.
  Six tabs over eleven statuses, no `all` tab, **no archive concept** (never re-run migration 003).
  v1-rubric rows show `v1`, not a number. Group headers are `<date> — N seats` only. Counts derive
  from the rendered rows. Under plain `http.server` the page says the list is unavailable.
- `jobs_tracker` (v1, 92 seats) is frozen and never opened; `jobs_tracker_v2` is v2. Verify both
  read-only: `psql -d postgres -f db/verify.sql`. `automation/jobs_db.py` is read-only;
  `automation/jobs_sync.py` registers a seat and refreshes scores from `score.json` (idempotent;
  never overwrites a five-axis breakdown).
- **All SQL lives in `db/` and is re-runnable.** Operations in `db/operations/`: `mark_applied.sql`
  (its usage comment is wrong — pass `set_config('mark_applied.slug',…)`), `set_status.sql`,
  `withdraw.sql`, `set_source_url.sql`, `log_event.sql`, `clone_seat_resume.sql`. For text containing
  quotes, put the `set_config` select in a scratch `.sql` file (dollar-quoted) and run
  `psql -f that.sql -f db/operations/<op>.sql`.
- **Timeline (`application_events`):** log every InMail, reply, document and call. `actor` is
  required (the named person, or "Abhisheik"); `detail` is verbatim; `artefact` is the repo path
  when a file changed hands. Append-only: correct by adding an event.
  ```
  psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('ev.slug','<slug>',false), set_config('ev.kind','inbound',false), set_config('ev.actor','<who>',false), set_config('ev.summary','<one line>',false), set_config('ev.detail','<verbatim>',false)" -f db/operations/log_event.sql
  ```
- **Server:** `automation/.venv/bin/python automation/serve.py` — port 8006, bound to 127.0.0.1,
  sends no-store, provides the state API. Never `python3 -m http.server`.
- **Daily log:** `daily/index.html` is generated from `daily/days.json` by `automation/daily.py`;
  state lives in PostgreSQL `v2_daily`. `./todo` coordinates and never executes. Moving a task out
  needs a reason (revivable only if every reason is revivable); unfinished tasks roll over; never
  duplicate one. Tests: `bash automation/tests/run.sh`.
- **Scaffold a seat:** `automation/.venv/bin/python automation/resume.py new --slug <slug> --url <url> [--company X --role Y]`.
- `automation/upgrad_resume_paste.py` is the shared résumé parser — load-bearing, never "clean it
  up". `automation/cleanup_cards.py` never runs unless he names a card.
- **upGrad / Hiration is retired** (access revoked 27 Aug 2026); every entry point exits 3 on
  purpose, so never diagnose that as a bug. History: `docs/RETIRED-upgrad-pipeline.md`. Keep
  `master/live_card_dump*` (the only record of the cards). Never send
  `master/Abhisheik_Deo_Resume.SUPERSEDED-2026-08-25.pdf`.
- No per-file `<style>`; shared classes live in `style.css` (`.page.full` is full width).
  Workspaces are `Month-YYYY/DD/<slug>/`, three levels below the repo root.

## Measurement traps
- Word counts ignore punctuation tokens. `grep -c` counts lines, not occurrences, and these files are
  minified. The LinkedIn URL sits in a PDF link annotation, not the text. A missing script throws
  nothing, so prove features work. Regex context windows give false positives: search case-sensitive,
  word-bounded and tag-stripped. Enumerate every source before concluding about "the" source. The
  local `grep` (ugrep) rejects long context patterns; use Python.

## Working rules
- **Ask, don't assume:** use `AskUserQuestion` with 2–4 options at forks, ambiguities,
  create-or-don't choices and identifier framing. The exception: a pasted JD always gets the full build.
- Never use browser automation or screenshots to check rendering; verify HTTP 200 and hand off.
- Audit agent output against the journey document. Rank findings by evidence; don't inflate a caution.
- Code-derived findings read a partial sample, and absence there is not absence in production. Ask
  him before saying code contradicts a claim.
- Check JD claims on the company's own site. A foreign city in a remote JD is usually a time-zone anchor.
- Relocation is open; 6- and 7-day weeks are fine; travel cadence and 24/7 on-call are worth surfacing.

## Interview prep
- **Lives in this repo**, in the job's own workspace beside `research.html`. **Never add anything to
  `~/Documents/interview-prep/`** (his rule, 28 Sep 2026). Reading it is fine — its honesty ledger is
  still the reference for what he may claim. What is there stays as it is, and its own "copy to
  both" rule no longer applies.
- When a job he has applied to asks for a topic that repo does not cover (for example C# or ASP.NET
  Core), **suggest it** in the conversation: the topic, where the JD asks for it, what is missing.
  *"just suggestions. nothing else."* — never a draft or a file.
- Rooms: headline sentence first, detail only if asked (CBRE round 1). Timed, out-loud, recorded
  practice beats more content; record every round. Never attribute the EVA rejection or the CBRE
  withdrawal to a cause.

## Session handoff and status
- Rewrite `RESUME_SESSION.md` wholesale whenever the context is about to clear or the picture changes
  materially. `PENDING.md` holds run IDs and analysis that outlives a session.
- Facts live in the database, never in this file:
  `psql -d jobs_tracker_v2 -c "select slug, company, status, fit_score, applied_at from applications order by fit_score desc nulls last;"`
- Company facts belong in each seat's `research.html` (older summaries are in the original file).
  `/last30days` found nothing on these employers in August 2026, so never claim social buzz.
