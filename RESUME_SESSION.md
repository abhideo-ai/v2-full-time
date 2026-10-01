# RESUME_SESSION.md

Where we were, and what is next. Overwrite freely; git keeps the history. Rules: `CLAUDE.md`.
Also: `PENDING.md`, `db/README.md`. **Last rewritten: 2026-10-01**, before he cleared context for a new session.

## START HERE (1 Oct 2026, before the new terminal session)
- **The server is RUNNING, detached** (PID 48641, parent launchd): it survives the session and
  serves http://localhost:8006 until a reboot or `kill $(lsof -tiTCP:8006 -sTCP:LISTEN)`. Check
  with `lsof -nP -iTCP:8006 -sTCP:LISTEN`; if nothing listens, start it detached:
  `(nohup automation/.venv/bin/python automation/serve.py > /tmp/serve.log 2>&1 < /dev/null &)`.
- **Nothing else is running.** Everything is committed and pushed (branch `qa`).
- **Plan mode trap (30 Sep):** if plan mode is on when a workflow starts, its agents can only read
  and write nothing. Check before launching.
- **New jobs:** he drops a `jd-list/<folder>/<file>.md` or pastes a post (goal: one workflow per job,
  capped at 3 agents). Scaffold (`resume.py new --url …` or `--no-url "<reason>"`, copy
  `templates/workspace/index.html`, write `workspace.json` with the `mismatch` tab and, for a
  DM/email route, an `email`/`dm` tab; save the paste word for word to
  `job-applications/<Month-YYYY>/<DD>/<slug>-intake.md`; log the arrival; clone the seat résumé),
  then run `automation/workflows/seat-workspace.js` with Workflow `scriptPath` and per-seat `args`
  (slug, short, **dir, date, date_text**, company, role, location, mode, url, screenshot, research,
  glossary, score, optional extra_tabs / extra_research / extra_score / extra_check). The last run's
  args are in its journal (`PENDING.md` has the run IDs). Then adjudicate here, apply edits with
  `db/operations/seat_edits_<slug>.sql`, generate and verify the `.docx`, fix the pages,
  `check_workspace.js`, `jobs_sync.py`, commit and push.
- **When he says one went:** `mark_applied.sql`, log an `outbound` event, then suggest the JD topics
  the interview-prep repo lacks ("just suggestions").
- **He exports PDFs himself** from Word; never automate it. His last pay was ₹60L fixed + ₹12L
  variable, he is accepting offers now, and his current pay is never volunteered (memory).

## Open applications
| Seat | State | What is next |
|---|---|---|
| **GetHyr, Engineering Manager / Sr EM** (`September-2026/29/gethyr-engineering-manager/`) | He decided to apply (30 Sep), **not yet sent** | He sends the Email draft tab's email to raj@gethyr.com with his `.docx` (he retitled the 2025–26 VoltusWave role "Vice President of Technology" himself in Word; the seat row matches; 35/35). Current CTC is a placeholder, his call. When sent: mark applied. Client unnamed; technical 92.83. |
| **Eli Lilly, Sr. Principal Engineer AI/ML System Integration** (`September-2026/29/eli-lilly-sr-principal-engineer-ai-ml-integration/`) | Ready, unsent | Tailored from the OLD master; send as is (87.90) or re-tailor from the new master: his call. Workday R-112121, open until 28 Oct 2026. |
| **Tachyon, AI Architect** (`September-2026/24/tachyon-ai-architect/`) | heard_back; he **confirmed 65 LPA fixed** on 30 Sep after a call | Waiting for Bhargav to confirm "fixed" and give the next steps (interviews). Topics to learn: its own tab. Interview prep only when he asks. His pay: ₹60L fixed + ₹12L variable (memory); he is accepting offers now. |
| **Recruise, AI Architect – Healthcare AI Platform** (`September-2026/30/recruise-ai-architect-healthcare/`) | Ready, unsent | Technical 89.78 (master 88.43). Email to shwetha@recruiseglobal.com staged in the Email draft tab (subject exactly “AI Architect – Healthcare AI”). Recruiter verified (registered company; her title matches Recruise's own site); client and city unnamed; post asks 13–16 years (he has 19+) and prefers Big Tech. |
| Nielsen PMTS (`September-2026/28/...`) | heard_back | See "Waiting on him — Nielsen" below. |
| Sent 29 Sep: Sahaj (84.90), Epiq (85.45), Zenvyra co-founder (85.88; route not stated) | applied, frozen | Wait to hear back. Topic suggestions already given. |

## His decisions still pending
1. **CLAUDE.md is stale:** it still lists the GNN, the 100,000 / P95 16 ms wording, the 70–80% and the
   four Rocket metrics as open claims, and Kubernetes among his confirmations. He settled all of these
   on 29 Sep (end of `professional-journey.md`; Kubernetes now off the résumé). Asked several times; no
   answer yet. Until he says, new pages mention them but do not lean on them.
2. **Master acronym fixes, offered 30 Sep, unanswered:** spell out P95 / P99 (95th- and 99th-percentile),
   JSON (JavaScript Object Notation), and SDE / VP in job titles. A two-minute fix if he says yes.
3. **Teletext 46% and $1.4M a year:** the $1.4M comes from a third-party profile whose link was never
   recorded (journey 429, 818), so it stays off; whether the 46% belongs to the Artirix replacement is
   unconfirmed.
4. **Recruise:** did he use classical ML libraries (scikit-learn, PyTorch, pandas) for the relapse
   model? Only that would lift its score; it is not in the record.
5. **Lilly:** send as tailored from the old master (87.90), or re-tailor from the new master.

**Settled 30 Sep (for the record):** the master now says "Vice President of Technology" for 2025–26
and names Python/FastAPI, the axe MCP server at Deque (2024), CloudFormation, microservices since 2016
and REST since 2013 (`db/operations/apply_master_2026_09_30.sql`; backup `variant:master-2026-09-30`);
it is 3 pages by his own PDF export. Claude at Deque came through Anthropic being a Deque accessibility
client with an early MCP preview: **interviews only, never in writing** (his rule; journey, "His
answers, 30 September 2026").

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
  ("His answers, 29 September 2026", which wins over earlier lines) and were applied by
  `db/operations/apply_story_clusters_answers.sql`, then promoted by
  `db/operations/promote_variant_to_master.sql`. `master/Abhisheik_Deo_Resume.docx` is the new master (35/35).
- The old master is kept as doc_key `variant:master-2026-09-29` and
  `master/Abhisheik_Deo_Resume.master-2026-09-29.docx`. Sent seats keep the résumés they were sent with.
- Three of his answers disagree with another source (flagged in the journey, kept as he said):
  P95 16 ms vs `img.png` 19.05 ms; the 70–80% vs his 14 Sep "No idea"; guardrails in production vs
  the case-study index's "pending".

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
