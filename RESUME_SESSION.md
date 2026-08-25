# RESUME_SESSION.md

**READ THIS FIRST at the start of every session.** This is the session handoff — what was in flight
when the last context was cleared, and what to pick up.

**Rewrite it whenever the context is about to be cleared, and whenever the picture changes
materially.** It is a living file, not a log: it describes the CURRENT state and the NEXT action.
Overwrite freely — git carries the history. Keep it readable in a minute.

**Last rewritten: 2026-08-25 ~23:55.**

**The other two files that matter:** `CLAUDE.md` is the rulebook and carries a Status section;
`PENDING.md` holds run IDs and analysis that outlives a single session.

---

## THE JOB WAITING FOR YOU

**SEND SOMETHING. Nothing has gone out.**

Three tailored, verified PDFs now exist and one recruiter reply is staged and unsent. The build side
of the loop is done for these four seats. The send side has not started.

**Cheapest single action: he pastes `August-2026/25/wipro-principal-software-architect/reply.html`
into LinkedIn.** Verified, carries his number, offers Thursday 27 August.

---

## Current state — BUILT AND EXPORTED

```
August-2026/25/yes-madam-lead-architect/            pdf=YES  score=88.375  tailored=YES  sent=no
August-2026/25/principal-architect-ai-native/       pdf=YES  score=84.9    tailored=YES  sent=no
August-2026/25/o9-senior-architect-agentic/         pdf=YES  score=81.4    tailored=YES  sent=no
August-2026/25/wipro-principal-software-architect/  pdf=no   score=NONE (no JD)  reply=STAGED, unsent
```

All three PDFs: **3 pages, ATS 85, no `[fill in metric]`, VoltusWave ends Apr '26**, LinkedIn slug
`abhisheikdeo` — which lives in a **PDF link annotation, not extractable text**, so a text-only grep
reads it as missing. That is a false alarm; check the annotations.

**They are genuinely different documents**, which was the whole point: Yes Madam carries Kubernetes,
Terraform, HIPAA and load balancing; o9 carries Python, DuckDB, Parquet and SageMaker; AI-Native
carries the retrieval stack and the shared-platform ledger.

---

## What changed, and why the scores moved

**Yes Madam went 83.0 → 88.375 without a single new claim** — all of it work he had already done that
was missing from the résumé.

| Confirmed 2026-08-25 | Consequence |
|---|---|
| **Kubernetes + Terraform real**, and **adopted as a company-wide standard** | Yes Madam's 2.25-pt "unrecoverable" Kubernetes cap → zero. AI-Native standards-adoption 7.5 → 8.5 |
| **High-availability design real** — multi-AZ, failover, disaster recovery | Another 2.0-pt floor removed |
| **The certification is HIPAA** | Bullet names it instead of "a certification requirement" |
| **He owned load balancing** | A JD-*required* line that had scored zero |
| **All 17 VoltusWave bullets accurate** — *"everything is accurate"* | The whole merge pool became usable |

---

## THE CARD TRAP — read before touching any card

**TWO live Hiration cards carry DIFFERENT VoltusWave blocks.** A full session was lost to this.

- `august_ic_master_resume` (**the export default**) — VoltusWave = **10 bullets**, identical to
  `master/upgrad_resume.html`. No Kubernetes, no Terraform, no Fargate, no k6.
- `august_master_resume` — VoltusWave = **17 bullets**. **This is the block every handoff note ever
  meant**: Kubernetes, Terraform, ECS Fargate at 70% Spot, k6, React Native across 2 app stores, the
  four named archetypes, `TraversalSource`, Rosenbaum gamma + E-value.

**Dumping only the IC card produces a confident, wrong conclusion that the 17 bullets do not exist.**
Both are now on disk and committed:

```
automation/.venv/bin/python automation/dump_card.py [--card NAME]   # READ-ONLY, never writes
  -> master/live_card_dump.json / .md              (august_ic_master_resume)
  -> master/live_card_dump_august_master.json/.md  (august_master_resume)
```

**The real card-versus-master gap is DEQUE**, not VoltusWave: both cards carry **14** Deque bullets,
the master carries **6**.

---

## STILL HIS HAND

- **The merge into `master/upgrad_resume.html`.** `master/merge_proposal.html` stages it as
  whole-section copy blocks: **24 merged VoltusWave bullets + 11 Deque, 35 unique leading verbs, all
  25 words or fewer.** The per-seat résumés already draw from it, but the **master still has zero
  hits for Kubernetes, Terraform, Jenkins, GitHub Actions, k6 and Fargate.**
  - **It is a POOL, not a drop-in** — 35 bullets where those roles carry 16 today, and the file is
    already 3 pages at 39.
  - **Variants A and B** differ on exactly two bullets. All three seats used **B** (targets framed as
    *designed to*, per the honesty rule). Switching to A is his election, never a default.
- **El Paso's three card bullets still read .NET.** Title is fixed; bullets revert on save. Correct
  text: `master/upgrad_resume.html` section 14.
- **The +65% hotel conversions** — unresolved; stays per the no-scrub rule.

---

## HONESTY — the constraints that govern every bullet

- **No Amura outcome metrics exist.** Every figure in those case studies is a **pre-registered
  acceptance target**. Scale and design markers are fine. **Never present a target as achieved.**
- **The worst landmine: KQ2's illustrative served-cell table** — `412 / 217 / 0.58 / 0.34 / +24pp /
  max SMD 0.08`. Formatted exactly like a measured result; the page itself says *"Illustrative
  response shape, not a production measurement."* **None of those numbers may ever appear as an
  outcome.**
- **Amura names NO message broker** — `Kafka` and `Kinesis` both return **0 hits** across all 22
  case-study files. The Kinesis work is the **chat platform**, a separate system. Never conflate.
- **The 6-hour cache TTL is KQ4's**; KQ1 is 1h.
- **HIPAA has zero occurrences in the case-study corpus** — unverified, not false, so it **stays**.
  Flag it in prep.
- **Never claim:** Kafka, MongoDB, ClickHouse, Azure, Google Cloud Platform, SOC 2, Spring
  Cloud/WebFlux/Batch, **Grafana, Prometheus**. MySQL is historical (2015) only.
  **Kubernetes, Terraform, Redis and the graph neural network ARE claimable.**
- **Never retroactively scrub a submitted claim.** Unverified is not the same as false.

---

## DO NOT

- **Do not build interview prep.** The trigger is a company responding — not a score, not a PDF.
  Stopped run: `wf_58f6f5c4-caa`.
- **Do not research, surface or gate on COMPENSATION.** His directive: *"forget about compensation…
  it'll come up when we hear back and get to that stage."* All three `score.json` files and
  `research.html` are already purged of it.
- **Do not source seats.** He pastes; we build.
- **Do not re-rank unasked** — but a direct "which suits me best" IS a request; answer it.
- **Do not run `cleanup_cards.py`.** Ever, until he names a card.
- **Do not trust CLAUDE.md's verb pool list** — it was stale and nine "free" verbs were already in
  use. Regenerate from the file.

---

## Quirks worth not rediscovering

- **`upgrad_resume.html` is gitignored everywhere except `master/`.** So `resume.py sheet`'s git-diff
  change detection is blind to workspace edits. **This does not block exporting** — the exporter
  reads `upgrad_resume.html` directly and never touches the paste sheet.
- **`resume.py new` used to copy the master's `href="../style.css"`** into workspaces three levels
  down, leaving every workspace résumé unstyled. Fixed at the source 2026-08-25.
- **The launcher's tabs already work** — `static/tabs.js` fills counts and filters. The zeros in the
  markup are pre-script placeholders.

---

## ⚠ URGENT — YOUR POSTGRESQL IS ONE RESTART FROM NOT COMING BACK

**The running server's binaries have been deleted.** Verified 2026-08-25:

- The live process is `/opt/homebrew/opt/postgresql@16/bin/postgres` — **that path no longer exists**
- Homebrew now has `postgresql@18`; the 16 keg was removed while the 16 server was still running
- Data lives in `/opt/homebrew/var/postgresql@16` — 96 applications, the daily state, everything
- **Every `UPDATE` on `applications` already fails** — the `BEFORE UPDATE set_updated_at()` trigger
  cannot load `$libdir/plpgsql`. `v2_daily` has no triggers so the daily log is unaffected.
  `jobs_sync.py` works around it by setting `updated_at` explicitly with triggers off.

**A backup was taken while the server was still up:** `~/pg-backup-2026-08-25/all-databases.sql`
— 1.7 MB, 96/96 application rows, all four databases, no errors.

**Fix:** `brew install postgresql@16`. Until then, do not restart PostgreSQL or reboot without
expecting to reinstall first.

---

## The launcher now renders from PostgreSQL

`GET /api/jobs` in `serve.py`, backed by `automation/jobs_db.py` (read-only) and
`automation/jobs_sync.py` (the write side, deliberately a separate module so the one `serve.py`
imports cannot mutate v1's record). Search box and score columns added; `salary` is never in the
payload, per the compensation deferral.

**Counts total exactly 96** — building 7 · ready 14 · sent 10 · responded 0 · interviewing 1 ·
parked 15 · closed 49 · not-selected 0.

⚠ **`recommended_skip` (49 rows) maps to `closed`** — deliberately. In `parked` they would bury the
few builds he actually paused; in `ready` they would corrupt the ready-and-unsent count, which is
the backlog gate. `tab_for()` raises rather than dropping a row.

⚠ **The two score columns use different rubrics and are NOT comparable.** v2 seats carry the weighted
technical score; v1 seats are a rescale of their own five axes. Every row carries `rubric`.
**This rescale is an agent's interpretation of v1's axes, not his — worth his review.**

⚠ **`serve.py` must be the thing on port 8006.** It was found running as plain
`python3 -m http.server 8006`, bound to `*:8006`, which is why the daily log had been silently
falling back to localStorage and `v2_daily` had 0 rows. Restart it with:
`automation/.venv/bin/python automation/serve.py`

**Re-sync scores after any re-score:** `automation/.venv/bin/python automation/jobs_sync.py --scores`

---

## Rewriting this file

Replace the contents with: **THE JOB WAITING** (the single next action, his words where possible) ·
**Current state** (concrete: paths, yes/no) · **How to do it** (commands, what must be delegated) ·
**Honesty constraints** in flight · **Still his hand** · **DO NOT**. Then commit. If the next session
opens this file and still has to ask "where were we", it failed.
