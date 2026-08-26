# RESUME_SESSION.md

**READ THIS FIRST at the start of every session.** What was in flight when the last context was
cleared, and what to pick up.

**Rewrite it whenever the context is about to be cleared, and whenever the picture changes
materially.** It describes the CURRENT state and the NEXT action. Overwrite freely — git carries the
history. Keep it readable in a minute.

**Last rewritten: 2026-08-26 ~18:15.**

**The other files that matter:** `CLAUDE.md` is the rulebook and carries a Status section;
`db/README.md` documents the databases and the query cheatsheet; `db/DESIGN-bullets.md` is the
not-yet-built forward architecture.

---

## THE JOB WAITING FOR YOU

**Two seats are built, verified and unsent. Both have a named human to write to.**

1. **Condé Nast (87.4)** — `reply.html` is written and waiting. **This is the third encounter with
   this seat.** v1 built it 21 Jul (scored 96, never applied) and again 6 Aug after an inbound
   InMail from **Lokesh Reddy Guntaka**, in-house Talent Acquisition Lead — and that reply was never
   sent. Twenty days passed and the seat was reposted. The new reply apologises for the delay in one
   line, corrects v1's wrong "Bengaluru" to Hyderabad, answers every field he asked for **except
   current CTC**, and offers Friday 28 August. **This is the warmest route in the pipeline.**
2. **Keyloop (89.6, the highest score)** — PDF verified, no outreach contact identified yet.
   Applying is through the posting.

**Also open:** Wipro's reply to Harisri Parthasarathi, staged yesterday and still unsent. And Paul
Abbott (Andela) was told Abhisheik was interested before the seat was withdrawn — a two-line note
closing that loop keeps the Andela door open.

---

## The board — query it, never read it off filenames

```sql
psql -d jobs_tracker_v2 -c "select slug, status, fit_score, applied_at from applications order by fit_score desc nulls last;"
```

| seat | status | tech | sent | contact |
|---|---|---|---|---|
| keyloop-principal-architect | **ready** | **90** | — | — |
| modmed-senior-software-architect | applied | 89 | 16:45 | Prabhakar Teguri (in-house) |
| yes-madam-lead-architect | applied | 88 | 11:37 | — |
| conde-nast-principal-engineer | **ready** | 87 | — | **Lokesh Reddy Guntaka (in-house)** |
| principal-architect-ai-native | applied | 85 | 16:36 | — |
| o9-senior-architect-agentic | applied | 81 | 12:19 | — |
| wolters-kluwer-…-ai-platform-engineer | withdrawn | 70 | — | Paul Abbott (Andela) |
| wipro-principal-software-architect | awaiting JD | — | — | Harisri Parthasarathi |

**Four sent on 26 August.** That column was empty that morning. v1 died with 23 built and unsent.

**Every seat has a verified PDF except Wipro**, which has no job description and therefore no score —
inventing rubric criteria from a job title is the failure to avoid.

---

## What changed structurally today — read before touching the tooling

- **v1 and v2 are SEPARATE DATABASES.** `jobs_tracker` is v1's frozen 92-row record; **nothing in v2
  opens it.** `jobs_tracker_v2` holds v2's seats. All SQL lives in **`db/`** — `db/migrations/`
  (001–011), `db/schema.sql`, `db/verify.sql`, `db/operations/`, `db/README.md`.
  Health check: `psql -d postgres -f db/verify.sql`.
- **`db/operations/` holds the re-runnable commands** — `mark_applied.sql`, `withdraw.sql` (refuses
  without a reason), `log_event.sql`, `set_source_url.sql` (refuses a non-URL).
- **`application_events` is the correspondence timeline** — six kinds, a REQUIRED actor, and `detail`
  holding messages **verbatim**. Paul Abbott's and Harisri's InMails are stored in full. **Log an
  event every time something happens.** This is what v1 never had.
- **PostgreSQL was migrated 16 → 18.** The 16 server had been running since 19 Aug with its Homebrew
  keg deleted; every `UPDATE` was already failing. Backups in `~/pg-backup-2026-08-25/` and `-26/`.
- **`serve.py` binds BOTH loopback families.** macOS resolves `localhost` to `::1` first, so an
  IPv4-only bind let a stray `http.server` shadow the API silently. **Check with
  `lsof -nP -iTCP:8006 -sTCP:LISTEN`: one PID holding both addresses is healthy; two PIDs means a
  stray is shadowing.** ⚠ **Port 8006 is HIS.** Never bind or kill it; verify on your own high port.
- **`resume.py new` now REFUSES without `--url`**, or `--no-url "<reason>"` when a seat genuinely has
  none. It also rewrites BOTH `style.css` and `copy.js` paths on copy.
- **The launcher renders from `jobs_tracker_v2`**, v1-style tabs, counts derived by a
  `MutationObserver`. The daily log is a **Kanban board**; dragging a card out demands a reason.
- **Page shell is `--shell: min(1680px, 95vw)`** with prose capped at `--measure: 82ch`.

---

## ⛔ THE RULES THAT BIND EVERY BUILD

- **COMPENSATION IS DEFERRED.** Not researched, surfaced, scored, or gated on. It comes up when a
  company reaches that stage. Company financials (a firm's own revenue) are NOT compensation.
- **INTERVIEW PREP WAITS** until a company responds — then for that seat only.
- **NEVER CLAIM:** Kafka, NATS, MongoDB, ClickHouse, Azure, Google Cloud Platform, SOC 2, Spring
  Cloud/WebFlux/Batch, Grafana, Prometheus, Hazelcast/Ignite/Coherence, any cloud certification.
  MySQL is historical (2015) only.
- **CLAIMABLE (user-confirmed):** Kubernetes and Terraform (**adopted as a company-wide standard**),
  Redis, load balancing, **HIPAA**, the graph neural network, high-availability design (multi-AZ,
  failover, DR — **CHAT PLATFORM only, never Amura**), Docker, Amazon Kinesis (chat platform),
  OpenSearch, Elasticsearch `dense_vector`, FastAPI, Django, LangChain, LangGraph, real MCP servers,
  Node.js/Express, Datadog, ELK, infra cost −25–30%, deploy time under 10 minutes.
- **⚠ Spring Boot is SIX YEARS ACROSS TWO EMPLOYERS with a five-month gap** (Rocket Aug 2018–Jul
  2019, Deque Dec 2019–Feb 2025). **Never "six continuous years"** — that false claim was cut from
  the ModMed workspace today after surviving one verify pass.
- **⚠ Production Python is ~14 MONTHS.** This killed Wolters Kluwer (8+/5+ years required). It is a
  duration fact; no rewrite closes it.
- **No Amura outcome metrics exist.** Every case-study figure is a pre-registered acceptance target.
  **KQ2's illustrative table (412 / 217 / 0.58 / 0.34 / +24pp / SMD 0.08) is NEVER an outcome.**
  **Amura names no message broker** — the Kinesis work is the chat platform.
- **The agentic-scope split is an OPEN claim** — KQ1's claim grammar is live, KQ9's narrator ships
  off by default. Surface it; never resolve it. It is why Condé Nast scored 87.4 and not v1's 96.
- **He lives in HYDERABAD.** Relocation is not a constraint. 6- and 7-day weeks are fine.

---

## Measurement traps that have already cost time

- **A word counter must ignore punctuation tokens.** Counting the em-dash as a word reported 25-word
  bullets as 26. There are **zero** genuine over-length bullets in the repo.
- **`grep -c` counts LINES, not occurrences** — these files are minified. It reported 4 `span.note`
  uses when there were 63.
- **The LinkedIn slug lives in a PDF link annotation, not extractable text.** A text-only grep reads
  it as missing. Check the annotations.
- **Failures fail silently.** `copy.js` pointed at a nonexistent path in every workspace résumé —
  every copy button was dead — and it survived six workspaces because nothing errors.
- **⚠ There are TWO live Hiration cards.** `august_ic_master_resume` (export default) has 10
  VoltusWave bullets; `august_master_resume` has **17**, and that is the block every handoff note
  meant. Both are dumped to `master/live_card_dump*.json`. **Dump BOTH before reasoning about a card.**

---

## In flight / not done

- **`master/merge_proposal.html`** stages 24 merged VoltusWave + 11 Deque bullets for the master.
  **Not landed.** The master still has zero hits for Kubernetes, Terraform, Jenkins, GitHub Actions.
  It is a POOL, not a drop-in — 35 bullets where those roles carry 16.
- **`db/DESIGN-bullets.md`** — the database-as-source architecture he approved for **later**:
  *"we can implement this AFTER we're done. GOING forward, we do that."* Schema is prepared
  (migrations 010/011, `resume_bullets` holds 488 rows as a derived index, nothing reads it).
  **The round-trip proof PASSED** — 458 bullets byte-identical, 30 entity-spelling only, 0 text or
  tag differences, `<strong>` counts preserved exactly. Migration is safe on the evidence.
- **El Paso's three card bullets still read .NET.** His hand; correct text in `master/upgrad_resume.html` §14.
- **ModMed's résumé does not contain "domain-driven"** though the JD names DDD. Substance is there
  (the service-per-database boundary rule); the keyword is not. One-line change + re-export, his call.

---

## Rewriting this file

Replace with: **THE JOB WAITING** (the single next action, his words where possible) · **the board**
(queried, not guessed) · **what changed structurally** · **the binding rules** · **traps** · **not
done**. Then commit and push. If the next session opens this and still has to ask "where were we",
it failed.
