# CLAUDE.md — Full-time JD workspace (v2)

Rules only. How-to (commands, database, automation, traps): `docs/reference.md`. History:
`docs/CLAUDE-original-2026-09-28.md`. **Read `RESUME_SESSION.md` first.** Server: `automation/serve.py`.

## Purpose
- Individual-contributor (IC) seats only: Principal, Staff, Architect, Solution Architect, Senior
  Engineer. Never source a leadership seat or rank one into the apply-first queue — but every JD he
  pastes gets the full build; the only question is whether to send it.
- Sending is the goal: a build is done when sent, or parked with a reason. Past about five
  ready-and-unsent, say so.
- Never source seats. Never re-rank or recommend an order unless asked. Nothing outside this repo is
  in scope.

## When he pastes a job
1. Get the posting URL, or record why there is none. `source_url` is a URL or NULL, never prose.
2. Scaffold the workspace, save his paste word for word, log the arrival as an event.
3. Tell him the plan and the rough time.
4. **At most 3 agents for the whole job,** across all turns, including its interview prep; ask
   before using more: (1) research and JD pages · (2) scoring and résumé edits · (3) one adversarial
   check of every proposed claim. One agent covers every angle; batch small edits into one pass.
5. Adjudicate here and cut anything unsupported. Apply the edits in the database, generate and
   verify the `.docx`, then resume agent 2 with SendMessage for the rubric `index.html` and
   `resume_changes_for_<N>pct_match.html` (one copy block per organisation).
6. Report in two to four plain lines: done, needs his decision, still running.
7. When he says it went: mark it applied, log it, and suggest any JD topic the interview-prep repo
   does not cover.
- No JD: workspace, research and a landing page; no score or résumé yet. A recruiter message: stage a
  short reply.
- A full workspace: `jd.md`/`jd.html` · rubric `index.html` · résumé-changes page · cited
  `research.html` (never compensation) · `score.json` · the verified `.docx`. Every workspace needs
  an `index.html`.
- Delegate content to keep this CLI answerable; never poll. Main thread only: adjudication, the
  verify pass, his decisions. Deterministic checks are scripts, never agents. Outside a job: 5 per
  workflow and per turn.

## Honesty
- `professional-journey.md` is the truth; the master résumé derives from it and loses on conflict.
  His additions are intake: reconcile them, flag contradictions. Before restructuring anything he
  wrote by hand, copy it to `<name>-original.md` (check git status first).
- Never invent a number. He has no outcome numbers (he left VoltusWave before capturing them);
  never ask again. Safe markers: 80+ conditions, a 6-hour cache TTL (KQ4; KQ1's is 1 hour), a 90-day
  outcome window, twenty review findings in a hardened v2, 13 of 13 local findings closed, 9–10
  years of patient history.
- KQ2's table is illustrative: 412, 217, 0.58, 0.34, +24pp and 0.08 are never outcomes; nor is
  KQ1's "300 patients". Amura names no message broker; Kinesis is the chat platform's. All of the
  v1 case studies shipped.
- Status words are never upgraded: designed is not shipped, piloted is not production, a target is
  not a measurement.
- Open claims are his alone — the graph neural network, the four Rocket metrics, the 70–80%
  consolidation, the 27 ms / P95 16 ms pairing, the 100,000-concurrent wording. Surface them; never
  resolve them.
- His confirmations (Aug 2026): Kubernetes, Terraform, HIPAA, load balancing, high availability.
  The prep ledger disputes Kubernetes — open.
- Agents get about 1 claim in 10 wrong. Unsupported claims are cut, not softened; adjudicate the
  checker too.

## Résumé
- The database (`jobs_tracker_v2`) is the source. Query the database; never grep résumé files. He
  supplies material; nothing ships on his behalf.
- Every bullet: ≤25 words · a strong verb opener (never Managed / Replaced / Responsible for /
  Worked on / Helped) · a unique leading verb (same roots collide) · a number or scale marker · a
  bolded fact · no trailing period · every acronym expanded on first use. See `resume-issues-to-avoid/`.
- Rule 7: re-vector bullets per job across the current role and 2–3 prior; edit in place, keeping
  the verb; real work only.
- Per seat: start from the master and aim for 95+%, editing only the last five roles — VoltusWave
  (Principal), Deque, Rocket, VoltusWave (Co-Founder), Teletext India. Never a copied file. New jobs
  only: sent seats are frozen.
- Expand acronyms everywhere, chat included. An unfamiliar domain gets a glossary at the top of
  `research.html`. Call out collisions (SOC 2 vs a SOC; RAG = Red/Amber/Green).

## Scoring and pay
- Technical score, target 95+, honest: a weighted rubric with evidence; read "e.g. / or" generously;
  an unused named tool is a ramp item; name the binding constraint and the smallest lift. An honest
  88 beats an invented 95. Non-technical score: informational only. Gates (levelling, legitimacy)
  are named separately. Apply broadly.
- Compensation is deferred until a company asks: never research, surface, flag or score it; a JD's
  band goes into `jd.md` as a neutral fact. When asked: ₹75L–₹1Cr fixed (midpoint ₹87.5L). The
  current ₹72L is never volunteered; disclose it only when he says so.

## Voice and replies
- Human prose: no aphoristic closers, few em dashes, never "non-negotiable", "blast radius",
  "compounds over a career". Outward pieces lead with strengths and never volunteer gaps.
- Anything he will paste is staged as HTML with a working copy button.
- Recruiter replies: answer exactly what was asked, in order, with no extra questions; lead with
  "available immediately, nothing to serve"; give +91 93640 27487 when inviting a call; offer a
  slot about 2 days out, never tomorrow.

## Interview prep
- Lives in this repo, in the job's workspace. Never add anything to `~/Documents/interview-prep/` —
  reading its honesty ledger is fine, and what is there stays. For a job he applied to, suggest the
  topics that repo lacks: "just suggestions. nothing else."
- Rooms: headline sentence first, detail only if asked; record every round; never attribute the
  EVA rejection or the CBRE withdrawal to a cause.

## Working rules
- Ask with AskUserQuestion (2–4 options) at forks. A pasted JD is never re-asked.
- Never use browser automation or screenshots to check rendering; verify HTTP 200 and hand off.
- Rank findings by evidence. Code-derived findings read a partial sample: ask before saying code
  contradicts a claim.
- Check JD claims on the company's own site. Relocation is open; 6–7 day weeks are fine; travel
  cadence and 24/7 on-call are worth surfacing.
- Never: run `cleanup_cards.py` unless he names a card · re-run migration 003 · open v1's
  `jobs_tracker` · remove `upgrad_resume_paste.py` (the live parser) · revive upGrad (exit 3 is by
  design) · send the `SUPERSEDED-2026-08-25` PDF · hand-write launcher rows.
- Facts live in the database, never in this file. Rewrite `RESUME_SESSION.md` whenever the picture
  changes; `PENDING.md` holds run IDs. Commit and push when the work is done (branch `qa`).
