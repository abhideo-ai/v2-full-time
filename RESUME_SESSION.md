# RESUME_SESSION.md

**READ THIS FIRST at the start of every session.** This is the session handoff — what was in flight
when the last context was cleared, and what to pick up.

**Rewrite it whenever the context is about to be cleared, and whenever the picture changes
materially.** It is a living file, not a log: it describes the CURRENT state and the NEXT action.
Overwrite freely — git carries the history, so nothing is lost by replacing it wholesale. Keep it
short enough to read in a minute.

**Last rewritten: 2026-08-25 ~22:40.**

**The other two files that matter:** `CLAUDE.md` is the rulebook and carries a Status section;
`PENDING.md` holds run IDs and analysis that outlives a single session. This file points at both.

---

## THE JOB WAITING FOR YOU

**Build a tailored résumé for each of the three scored workspaces, in its own workspace,
then export and verify each PDF.**

He asked for this explicitly: *"I need a specific resume for each of these in their workspace."*

### Current state — scored, NOT tailored, NOT exported

```
August-2026/25/o9-senior-architect-agentic/      pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
August-2026/25/principal-architect-ai-native/    pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
August-2026/25/yes-madam-lead-architect/         pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
```

Only `master/Abhisheik_Deo_Resume.pdf` exists — 3 pages, ATS 85, verified.

**⚠ Do NOT export as they stand.** Each `upgrad_resume.html` is byte-identical to the master, so
three exports would produce three identical PDFs — precisely the top-of-résumé-only tailoring that
produced **zero calls in June 2026**.

---

## HOW TO DO IT

**Every workspace artefact is built by a subagent or workflow — no exceptions.** The reason is his:
*"we keep the main CLI free for other stuff."* Work in the main thread blocks the session; work in
a subagent runs in the background and he can keep pasting job descriptions. Scaffolding with
`resume.py new` is a command and stays in the main thread; the moment content goes *into* a
workspace, delegate it.

**What stays in the main thread:** adjudicating what comes back, the adversarial verify pass against
`professional-journey.md`, his decisions, and `./todo`.

### Per seat — Rule 7 re-vectoring

Edit bullets **in place, keeping the leading verb**. Only add a bullet with a verb confirmed free
across **all ten roles** (the card-only pre-2016 ones live in the same file and their verbs count —
missing that put `Hardened` and `Extracted` in two roles each).

**VoltusWave carries ten bullets and must come down to six or seven** for the three-page limit —
a *different* four dropped for each seat.

| Seat | Lead with | Cut |
|---|---|---|
| **principal-architect-ai-native** (83.3) | Elasticsearch `dense_vector` retrieval · the LangGraph orchestrator · self-hosted models in-VPC | Kinesis shards, Datadog, patient onboarding |
| **yes-madam-lead-architect** (83.0) | Java + Spring Boot · monolith → 10–15 services · Keycloak → Red Hat SSO · the Go concurrency work | most of the Amura AI bullets |
| **o9-senior-architect-agentic** (80.4) | data-engineering depth — event spine, Parquet/DuckDB, nine-year hydration — plus SageMaker retraining and drift | the chat-platform bullets |

Each `<workspace>/score.json` holds the full weighted rubric with evidence already quoted from his
own files, every gap labelled RAMP ITEM or CAPABILITY CAP, plus the adjudication.

### Then, per workspace

```
automation/.venv/bin/python automation/resume.py sheet --slug <slug>
UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py \
    --slug <slug> --no-pause --reset
```

The exporter runs **serially** on one shared browser. It is unblocked and proven end to end.

### Verify every PDF

Dates (VoltusWave **Apr 2026**) · bold renders heavier · LinkedIn slug **abhisheikdeo** ·
no `[fill in metric]` · **≤3 pages** · content matches the sheet. Ignore the ATS score — it moves on
hygiene, not fit, and he has said 85 is fine.

---

## HONESTY — the constraints that govern every bullet

- **No Amura outcome metrics exist.** He left before capturing them; every figure in those case
  studies is a **pre-registered acceptance target**, not a measurement. Scale and design markers are
  fine (ten services, 80+ conditions, 9–10 years of history, twenty review findings). **Never
  present a target as an achieved result.**
- **The 100,000-concurrent figure is BURST TESTING**, not sustained production load.
- **Never retroactively scrub a claim that has already gone out.** Unverified ≠ false. Before
  proposing any removal, say which it is; if you cannot, it is unverified and it **stays**.
- **Never claim:** Kafka (he has Amazon Kinesis), MongoDB, ClickHouse, Azure, Google Cloud Platform,
  SOC 2, Spring Cloud/WebFlux/Batch. MySQL is historical (2015) only.
  **Kubernetes and Terraform ARE claimable** — he confirmed both 2026-08-25; a previous handoff
  had wrongly listed Kubernetes as never-claim.
  **Redis IS claimable. The graph neural network IS claimable** — he confirmed both 2026-08-25.
- **Never fabricate to reach 95.** None of these three reaches it and none is closable by
  rewording — each is capped by absent experience. Say so plainly.

---

## STILL HIS HAND

- **El Paso's three bullets on the Hiration card still read .NET.** The title is corrected to
  *Senior Java Developer*; the bullets revert on save. Correct text is in
  `master/upgrad_resume.html` §14.
- **His live card's 17 VoltusWave bullets are not merged into the master** — Kubernetes, Terraform,
  ECS Fargate at 70% Spot, k6-validated, React Native across 2 app stores, the 4 reusable
  archetypes, `TraversalSource` wrapper, Rosenbaum γ + E-value. **Biggest unfinished résumé work,
  and it bears on Yes Madam directly: his live card claims Kubernetes and Terraform, which the
  master does not. If that is real, Yes Madam's binding constraint disappears. ASK HIM.**
- **The +65% hotel conversions** — unresolved; stays per the no-scrub rule.

---

## DO NOT

- **Do not build interview prep.** He stopped it: *"DO NOT build the prep now… we wait until I hear
  back from the company."* The trigger is a company responding — not a score, not a workspace being
  ready. Then build prep for **that** seat only. The stopped run is `wf_58f6f5c4-caa`, resumable.
- **Do not source seats.** He pastes; we build.
- **Do not re-rank or recommend an order** unless asked.
- **Do not re-litigate the vector-DB gap as a capability cap** — it is a ramp item and he is right.
- **Do not hand-paste résumé sections.** No markup gives both bold and bullets through a real
  clipboard; the exporter's `_paste_html` is the only path that keeps both. See CLAUDE.md,
  *Pasting into Hiration*.

---

## NOTHING HAS BEEN SENT YET

Sending is the north star, not building. Three scored workspaces and zero applications out is the
v1 failure in miniature — v1 died with 23 workspaces built and unsent.

See also: `PENDING.md` (the scores, the sharpest finding per seat, the ranked gap list) and
`CLAUDE.md` (the full rulebook, with Status current as of tonight).


---

## Rewriting this file

At the end of a session, or before a context clear, replace the contents with:

1. **THE JOB WAITING** — the single next action, in his words where possible.
2. **Current state** — what exists on disk, what does not. Be concrete: file paths, yes/no.
3. **How to do it** — the commands, and what must be delegated.
4. **Honesty constraints** that govern the work in flight.
5. **Still his hand** — what only he can do.
6. **DO NOT** — the things he has stopped, so they are not restarted unprompted.

Then commit. If the next session opens this file and still has to ask "where were we", it failed.
