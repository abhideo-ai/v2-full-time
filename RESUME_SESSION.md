# RESUME_SESSION.md

Where we were, and what is next. Overwrite freely; git keeps the history. Rules: `CLAUDE.md`.
Also: `PENDING.md`, `db/README.md`. **Last rewritten: 2026-09-28**, after the Delta build.

## First: is the server running?
`lsof -nP -iTCP:8006 -sTCP:LISTEN` — if nothing is listening, run
`automation/.venv/bin/python automation/serve.py` (it runs in Claude's shell; he is fine with that).

## Board — query it: `psql -d jobs_tracker_v2 -c "select id, slug, status, fit_score, applied_at from applications order by id;"`
- **Delta Technology (122)** — referral, role to be created, `interviewing`. Interview with Kim
  Batcheler (UK) not booked; the referring friend is not named. Delta is rebranding as Enhansd (its
  AI arm, "Studio", is not live yet). Workspace done: `September-2026/27/delta-technology-referral/`.
  Its prep pages sit in `~/Documents/interview-prep/study-plans/delta-technology-referral/`,
  committed there before the 28 Sep rule — leave them.
- **Harshita Vishnavam (121)** — applied 27 Sep through her form. A short follow-up reply is staged
  in `reply.html`, **not sent**; log an `outbound` event when he sends it.
- **Tachyon (116)** — applied 24 Sep, frozen.
- **Aezion (114)** — ask him whether the Sravan reply went; never assume.
- **Wipro (99)** — no JD since the 25 Aug InMail.

## Open — his call, not acted on
- Harshita: if a JD arrives, does an applied (frozen) seat still get a tailored résumé?
- Before any deploy of interview-prep: the Delta prep folder would publish research about a named
  private person (it is not in `.assetsignore`).
- To settle (section 9 of `your_stories_for_kim.html`): was the graph neural network ever served;
  Kinesis on-demand vs a shard number he chose; MySQL (journey l.383 Cura, l.526 axe Monitor) vs the
  prep ledger's never-claim; was the "~300" he told CBRE the instance count (settled: 280 axe Monitor
  clients); VoltusWave ↔ Amura in one sentence; Keycloak "zero disruption"; Redis in KQ10's stack.
- Master "Reimagined" bullet attaches "P95 under 30 ms" to PostgreSQL; the prep ledger says that
  figure belongs to the DynamoDB write path.
- Kubernetes: this repo lists it among his confirmations; the prep ledger lists it as never-claim.
- "ELK" is never expanded in the master (first use: quick-skills-ee 16).
- Tachyon carry-overs: were the 100+ golden queries clinician-graded? "Co-defined" or "Facilitated"?
- Phones: `dl.context-grid` never folds to one column (a shared CSS rule loses on specificity).
- `./todo` still carries `journey-doc` and the two Aezion tasks.

## Running notes
- Web search is capped at 200 per session; heavy research can use it all (curl still works).
- `ord` is part of `resume_blocks`' primary key: shift a section by +1000 before renumbering.
- A `.docx` page count cannot be checked here; he checks it in Word.
- `add_breadcrumbs.py` and `expand_acronyms.py` only scan `killer-query-case-studies/`.
- He says "commit & push ALL" after each piece of work; the branch is `qa`.
