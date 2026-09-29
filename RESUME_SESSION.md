# RESUME_SESSION.md

Where we were, and what is next. Overwrite freely; git keeps the history. Rules: `CLAUDE.md`.
Also: `PENDING.md`, `db/README.md`. **Last rewritten: 2026-09-29**, after the Lilly and Sahaj builds.

## START HERE (29 Sep 2026, afternoon)
- **Sahaj was SENT on 29 Sep 2026** (he said "application is done"; marked applied and logged; the seat is now frozen). **Lilly is ready and unsent.** **Epiq, Lead Software Engineer - AI Solutions** (Hyderabad; Epiq's record says hybrid, Hyderabad or Pune; Workday requisition R0035231) was SENT on 29 Sep 2026 (marked applied and logged; frozen): `September-2026/29/epiq-lead-software-engineer/`, technical 85.45 (master 82.68), bound by React and named DevOps tooling; over-levelling risk (8–12 years asked, he has about 18; a Staff/Solution Architect seat, R0035035, 12+ years, was posted the same day). Both came from `jd-list/sept-2026-29/sep-29-2026_1.md`, built
  with one 3-agent workflow each, run side by side (6 agents at once: his explicit call over the
  4-per-turn rule). Run IDs and outcomes in `PENDING.md`.
  - **Eli Lilly, Sr. Principal Engineer AI/ML System Integration** (Bengaluru East, on-site):
    `September-2026/29/eli-lilly-sr-principal-engineer-ai-ml-integration/`. Technical 87.90
    (master 84.28). Apply through Lilly's Workday, requisition R-112121, open until 28 Oct 2026.
  - **Sahaj Software, Principal Engineer** (Hyderabad, on-site; employees report 2–3 office days):
    `September-2026/29/sahaj-principal-engineer/`. Technical 84.90 (master 83.04), bound by
    test-driven development (TDD), which his record never names: "automated testing", never TDD.
  - Each has a verified `.docx` (35/35; page count is his to check in Word), the Tech mismatch as
    its own tab (his choice for both, 29 Sep), and a "Settle before sending" list on the résumé
    page: the 70–80%, P95 16 ms, "Java 11 yrs", Keycloak "zero disruption", P95 30 ms/100,000.
  - Seat résumé edits are re-runnable: `db/operations/seat_edits_<slug>.sql`.
- **The server is running in Claude's shell** (port 8006); it stops when the session ends.
- When he says one went: mark it applied, log it, and suggest JD topics the prep repo lacks.
- **Nielsen's Tech mismatch tab is key for his preparation** (his words, 28 Sep). It is its own tab,
  `mismatch.html`, listed in that workspace's `workspace.json` (Nielsen only, his choice):
  http://localhost:8006/September-2026/28/nielsen-principal-member-technical-staff/index.html#mismatch
- `jd-list/sep-28-2026_2.md` holds only its goal lines so far. When he adds jobs: one workflow per
  job, capped at 3 agents (his rule in that file), built from `templates/workspace/`.

## Waiting on him — Nielsen
`September-2026/28/nielsen-principal-member-technical-staff/` (Principal Member Technical Staff,
Mumbai; tracker `heard_back`, technical 86.39). No résumé: recruiter Deepti Adlakha is using his
Naukri profile (her call, 28 Sep 2026). His to do: check the consent email's sender domain, and
consent within 30 days or the profile is deleted; ask her which listing it is (a Bengaluru one
exists too); settle Kubernetes before any call. Interview prep only when he asks. The only
core gap that caps a score row is test-driven development: say "automated testing", never TDD.
- Faster scoring (28 Sep): he set `/effort high` as his default, and `score.json` is now numbers
  only (`templates/workspace/score.json`); `check_workspace.js` checks its arithmetic.
- ATS checkers he can use (his question, 28 Sep): Jobscan (résumé + a JD → match rate), Resume
  Worded, Teal. No single official ATS score exists; compare both résumés against the same JD.

## The master is now the story-clusters résumé (29 Sep 2026, his words: "make it master")
- He answered `master/story-clusters-questions.md`; the answers are in `professional-journey.md`
  ("His answers, 29 September 2026") and were applied to the draft by
  `db/operations/apply_story_clusters_answers.sql`, then promoted by
  `db/operations/promote_variant_to_master.sql`. `master/Abhisheik_Deo_Resume.docx` is the new master (35/35).
- The old master is kept as doc_key `variant:master-2026-09-29` and
  `master/Abhisheik_Deo_Resume.master-2026-09-29.docx`. Sent seats keep the résumés they were sent with.
- Kubernetes is off the résumé (ECS Fargate instead, his call). Still open: Teletext 46% and the $1.4M.
- Lilly (ready, unsent) was tailored from the OLD master; whether to re-tailor it is his call.

## Draft, 28 Sep 2026 — the résumé as story clusters (now promoted; see above) (his ask; "we're just drafting this version")
`master/Abhisheik_Deo_Resume_story_clusters.docx` + `master/story-clusters-review.html` (evidence,
30 "needs your words" questions, open claims). Built from doc_key `variant:story-clusters`
(`db/operations/clone_master_variant.sql`, then `apply_story_clusters.sql`); the master's rows
and `.docx` are unchanged. Nothing replaces the master until he says so.

## Done 28 Sep 2026 — the workspace page, then Nielsen on it
- Nielsen built with one workflow (3 agents, run `wf_37031923-139` in `PENDING.md`); every new
  workspace is checked with `node automation/check_workspace.js <Month-YYYY/DD/slug>`.

### The workspace page (plan: `~/.claude/plans/why-is-claude-md-17kb-clever-rabbit.md`)
- Every workspace's `index.html` is one shell, the same file everywhere (`templates/workspace/`);
  `workspace.json` names the seat and its own tabs; each tab is a standalone page shown inside it
  by `static/workspace.js`; `static/page-tabs.js` switches. Status and score come from
  `/api/jobs?slug=`. How-to: `docs/reference.md`.
- His two answers: sections are **moved, never duplicated**, and the résumé-changes page **keeps**
  `resume_changes_for_<N>pct_match.html` (named in `workspace.json`).
- Piloted on Delta: research sections 4–5 → `kim.html`, 3 → `enhansd.html`, 9 → `questions.html`
  (with the six open items), 1 → the Glossary fold of `overview.html`; `research.html` is folds
  only. Text check against the old two pages: 849 of 870 text blocks carried over word for word;
  the other 21 are navigation, file pointers that had to change, and three glossary entries that
  research's fuller ones already cover.
- `serve.py`'s listen backlog is 64 (socketserver's 5 reset the eighth parallel request, so a tab
  came up empty at random). Restart `serve.py` after editing anything it imports.
- Tests, read-only: `test_workspace.js` 113/113 and `test_jobs_db.py` 125/125. Every key check was
  proven able to fail by planting a fault first. Applied seats keep their old pages (frozen).

## First: is the server running?
`lsof -nP -iTCP:8006 -sTCP:LISTEN` — if nothing is listening, run
`automation/.venv/bin/python automation/serve.py` (it runs in Claude's shell; he is fine with that).

## Waiting on him (job status itself: query the database — see `CLAUDE.md`)
- **Harshita (121):** her follow-up reply is staged in `reply.html`, **not sent**. When he sends it,
  log an `outbound` event with the text.
- **Aezion (114):** ask whether the Sravan reply went; never assume.

## Open — his call, not acted on
- Find in page (Ctrl+F) searches only the open tab: hidden tabs are skipped. Chrome's
  `hidden="until-found"` would search every tab and jump to the match; a small `page-tabs.js`
  change, not made because rendering is not checked here.
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
- He says "commit & push ALL" after each piece of work; the branch is `qa`. Commit only our own
  paths when he has files staged mid-edit.
