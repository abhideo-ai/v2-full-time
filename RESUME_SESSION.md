# RESUME_SESSION.md

Where we were, and what is next. Overwrite freely; git keeps the history. Rules: `CLAUDE.md`.
Also: `PENDING.md`, `db/README.md`. **Last rewritten: 2026-09-28**, after the workspace-page build.

## NEXT ACTION — Nielsen is built; waiting on him
`September-2026/28/nielsen-principal-member-technical-staff/` (Principal Member Technical Staff,
Mumbai; tracker `heard_back`, technical 86.39). No résumé: recruiter Deepti Adlakha is using his
Naukri profile (her call, 28 Sep 2026). His to do: check the consent email's sender domain, and
consent within 30 days or the profile is deleted; ask her which listing it is (a Bengaluru one
exists too); settle Kubernetes before any call. Interview prep only when he asks.
- Faster scoring (28 Sep): he set `/effort high` as his default, and `score.json` is now numbers
  only (`templates/workspace/score.json`); `check_workspace.js` checks its arithmetic.

## Draft, 28 Sep 2026 — the résumé as story clusters (his ask; "we're just drafting this version")
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
