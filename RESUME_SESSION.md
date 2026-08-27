# RESUME_SESSION.md

**READ THIS FIRST at the start of every session.** What was in flight when the last context was
cleared, and what to pick up.

**Rewrite it whenever the context is about to be cleared, and whenever the picture changes
materially.** It describes the CURRENT state and the NEXT action. Overwrite freely — git carries the
history. Keep it readable in a minute.

**Last rewritten: 2026-08-27 ~14:45.**

**The other files that matter:** `CLAUDE.md` is the rulebook; `db/README.md` documents the
databases; `db/DESIGN-bullets.md` is the architecture that just landed.

---

## ⚠ TWO THINGS CHANGED TODAY THAT INVALIDATE OLDER NOTES

### 1. upGrad is gone. Exporting is manual, in Canva Pro.

His words: *"we're going to go away from upgrad's resume builder"* · *"I've a Canva PRO account
which I'll use for this purpose"* · *"resume exporting, etc will be manual going forward"* ·
*"do not remove the files. just remove the step from the automation workflow."*

- The seven card tasks are out of `daily/days.json`; **`canva-export`** replaces them and
  `verify-pdf` now gates a hand-built PDF. That is the ONLY gate left — nothing upstream enforces
  dates, bold, the LinkedIn slug or the 3-page cap any more.
- **All nine scripts and both Hiration cards stay on disk.** Legacy, not garbage.
  `cleanup_cards.py` is still never run.
- CLAUDE.md's seven upGrad sections are marked **SUPERSEDED**. Do not re-add the step.
- `fix-el-paso` is **resolved** by leaving — that defect lived on the card and cannot follow us.
- ⚠ Canva risk worth repeating to him: most templates are two-column, and a multi-column PDF is
  the classic ATS parsing failure. Single column, real text boxes, LinkedIn as a real link.

### 2. The database is the source for the MASTER résumé. HTML is generated.

His words: *"DB is the source. No more grepping, etc etc."*

```
automation/.venv/bin/python automation/resume_db.py load      # file  -> DB
automation/.venv/bin/python automation/resume_db.py generate  # DB -> HTML
automation/.venv/bin/python automation/resume_db.py verify    # READ-ONLY drift check
```

- **Round trip proven byte-identical** — render with no reload reproduces the master exactly,
  sha256 `c68dcd53…`, 217 `<strong>` preserved.
- **`verify` is READ-ONLY and must stay that way.** It used to call `load` first, which made its
  pass a tautology *and silently destroyed DB edits*. Both fixed and re-proven by mutation.
- **Retired bullets survive a reload.** They used to be deleted by it.
- **SCOPE: the master ONLY.** The eight per-seat résumés are still files. A sent one is never
  edited. Do not half-migrate.

---

## THE BOARD — query it, never read it off filenames

```sql
psql -d jobs_tracker_v2 -c "select slug, status, fit_score, applied_at from applications order by fit_score desc nulls last;"
```

| seat | status | tech | contact |
|---|---|---|---|
| keyloop-principal-architect | applied | 90 | — |
| modmed-senior-software-architect | applied | 89 | Prabhakar Teguri |
| yes-madam-lead-architect | applied | 88 | — |
| conde-nast-principal-engineer | applied | 87 | Lokesh Reddy Guntaka |
| principal-architect-ai-native | applied | 85 | — |
| o9-senior-architect-agentic | applied | 81 | — |
| wolters-kluwer-… | withdrawn | 70 | Paul Abbott (Andela) |
| wipro-principal-software-architect | awaiting JD | — | Harisri Parthasarathi |

**Six sent, backlog of one.** v1 died with 23 built and unsent; that pattern is broken.

---

## THE MASTER RÉSUMÉ — rewritten today, 39 → 64 bullets

Sourced from `professional-journey-original.md`. VoltusWave 24 · Deque 14 · Rocket 4 ·
VW co-founder 3 · Teletext 4 · CURA 3 · innRoad 3 · McDonald's 3 · El Paso 4 · LyntonWeb 2.
Skills 25. **64 distinct leading verbs, zero collisions. Zero bullets over 25 words.**

**Three open claims HE settled today — do not re-ask, do not re-flag:**

- **innRoad = AngularJS**, not Angular. Supersedes `Knockout.js` on both live cards.
  ⚠ AngularJS 1.x is NOT modern Angular; this does not close the Angular gaps that docked
  earlier seats.
- **axe Monitor = 280 clients**, plus ~50 internal instances (testing, demos) OUTSIDE the 280,
  with migrations run across every instance. `300+` was FALSE and is gone.
  ⚠ **He has NOT stated a total.** 280 + ~50 implies ~330, which is *higher* than the ~300 he
  told CBRE — so ~300 may have been the instance figure. Ask; never guess.
- **Aurora PostgreSQL** — settled the platform without needing an edit. Aurora is an RDS engine,
  so the wording was already true. One word added: `major-version`.

---

## THE JOB WAITING FOR YOU

**Four structural findings from the review panels, surfaced and NOT acted on. His call.**

1. **The VoltusWave return is never explained.** Sections 6 and 9 are both VoltusWave, eight years
   apart; on the page he appears to go Co-Founder & VP → Principal Architect at the same company.
   Six words in the summary closes it. **Biggest narrative hole in the document.**
2. **The screener's window evidences nothing the headline promises.** Bullets 1–5 are all the chat
   platform, three carry `100,000`, two print competing P95 figures (16 ms / 30 ms) for one event.
   Kubernetes lands at bullet 23; Claude Code + Codex sits LAST in three separate blocks.
3. **Five years at Deque reads as generic SaaS** — `accessib` appears once in the section, and
   `axe Auditor` once in the whole document, as the object of a database upgrade.
4. **The summary's first eight words restate the headline** near-verbatim.

Also open: `vp#17` is the only bullet with no quantifier (documented, protected by the no-scrub
rule), and nine bullets carry two acronyms against the reference's cap of one — mostly unavoidable
product pairs like `.NET` + `SQL Server` on low-weight roles.

---

## RULES THAT BIND EVERY BUILD

- **COMPENSATION IS DEFERRED** until a company reaches that stage.
- **INTERVIEW PREP WAITS** until a company responds, then for that seat only.
- **NEVER CLAIM:** Kafka, NATS, MongoDB, ClickHouse, Azure, GCP, SOC 2, Spring
  Cloud/WebFlux/Batch, Grafana, Prometheus, Hazelcast/Ignite/Coherence, any cloud certification.
- **Spring Boot is SIX YEARS ACROSS TWO EMPLOYERS with a five-month gap** — never "six continuous".
- **Production Python is ~14 MONTHS.** No rewrite closes it.
- **No Amura outcome metrics exist.** KQ2's illustrative table (412/217/0.58/0.34/+24pp/0.08) is
  NEVER an outcome. Amura names no message broker; the Kinesis work is the chat platform.
- **UNVERIFIED stays, FALSE comes off.** Say which before proposing any removal.

---

## Rewriting this file

Replace with: what changed structurally · the board (queried) · the master's state · the single
next action · the binding rules. If the next session opens this and still has to ask "where were
we", it failed.
