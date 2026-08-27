# CLAUDE.md — Full-time JD Workspace (v2)

Tailored résumés + job descriptions (JDs) for **individual-contributor (IC) engineering roles**.

This is a deliberate restart. v1 is abandoned and nothing outside this directory is in
scope — everything this workspace needs already lives here. Nothing here is derived from v1
except the automation, the shared assets (`style.css`, `static/`, `resume-issues-to-avoid/`),
the journey document, and the rules below. **`professional-journey.md` is v1's file
byte-for-byte** and still carries every unresolved `OPEN →` marker v1 recorded, plus a 20-item
open-question list at its end. Resolve those before deriving the master. Two things changed,
and they are the whole reason v2 exists.

---

## The two changes that define v2

### 1. IC only. Completely.

**Source and build Principal / Staff / Architect / Solution Architect / Senior Engineer
seats. Nothing else.** Not Director, not VP, not Head of Engineering, not Engineering
Manager.

**Never source a leadership seat, and never rank an inbound one into the apply-first queue.**
But a leadership seat that *arrives* — he pastes it, a recruiter reached him first — still gets
the normal full build, with no re-asking. That fork is permanently closed: every pasted JD gets
built. The question worth asking is whether to **send** it, never whether to build it.

The evidence behind this: v1 submitted 28 leadership applications against 3 IC ones, and
**both processes that reached late-stage interview rounds were the IC ones** — while 11 built
IC workspaces sat unsent. **The defect was the effort ratio, not a measured performance gap.**
Do not quote IC-vs-leadership response rates as if they were significant: n=3 on the IC side.
IC seats had not underperformed; they had barely been tried.

### 2. Sending is the north star, not building.

v1 died with **23 rows sitting in the "ready" tab, unsent** — at most ~17 of them genuinely
submit-ready, since three have no exported PDF at all, one still carries a stale date, and two
are duplicate pairs. The backlog was diagnosed at 20 on 30 July and had grown to 23 by
24 August — a known problem that got worse. Meanwhile the response rate was fine: **~31 sends
produced ~13 responses, roughly 40%.**

**The bottleneck was never résumé quality. It was throughput.**

So:

- **A build is not done when it exports. It is done when it is sent, or explicitly parked
  with a written reason.** "Ready" is not a resting state.
- **Backlog gate — a judgement call, not a measured threshold.** Once ready-and-unsent passes
  roughly five, say so out loud and clear the backlog before adding to it. **This never blocks
  a build**: the gate governs what gets *attention* next, not what gets built.
- **Full build for every pasted JD, without exception and without re-asking.** That discipline
  produced the assets that actually worked. But finish the loop.

**A full workspace is:** `jd.md` / `jd.html` + card screenshots · weighted-rubric `index.html` ·
`resume_changes_for_<N>pct_match.html` · `bullets_for_upgrad.html` · `upgrad_resume.html` ·
cited `research.html` (verdict, red/green flags, comp reality, forcing questions) · then the
exported **and verified** `Abhisheik_Deo_Resume.pdf`.

---

## The résumé is derived from the journey document

**`professional-journey.md` is the source of truth. The master résumé is DERIVED from it
and loses when they disagree.** v1's master was assembled from bits and pieces; this one
is not.

He is actively enriching the journey doc with more detail — roles, tools, decisions,
numbers — specifically so the JD matching gets sharper. **Treat every such addition as
first-class intake work**, not as a side note: read it, reconcile it against what is
already claimed, and flag contradictions rather than smoothing them over.

**Before restructuring anything he wrote by hand, copy it to `<name>-original.md`
verbatim — typos included — and point to it from the derived file.** He has said, of an
earlier rewrite, *"after your changes I'm unable to recognise it."* Check `git status`
first: an `M` means the on-disk version is not recoverable from git.

`master/upgrad_resume.html` is **the single master résumé** — one file with two readers. He pastes
sections 1–15 into the Hiration card by hand; `upgrad_resume_paste.py` parses ten of them by id for
the bot. It replaced the old three-file split (parsed copy, hand-paste copy, blank template) on
2026-08-25, because sections 1–10 were duplicated verbatim and drifting apart silently. Every bullet
is a standalone `<p>`, never a `<ul>` — upGrad strips bold from list-rooted content — and the parser
now accepts both shapes. See `master/README.md` for the ten-section contract.

---

## Honesty — load-bearing

If it is not in the journey document and not user-confirmed, do not write it. A missing
metric is `[fill in metric]`, never an invented number.

**Never claim:** Kafka (he has **Amazon Kinesis**, confirmed in production), MongoDB,
ClickHouse, Azure, Google Cloud Platform, SOC 2, Spring Cloud, Spring WebFlux,
Spring Batch. Only **Spring Boot** is his.

**Redis was removed from that list on 2026-08-25, by him.** The Amura case studies place it
in the production request path of systems he owned — KQ4's per-tenant-namespaced risk cache
(TTL 6h) and KQ10's canonical keyed cache, both `FastAPI + Redis`. He confirmed the entry was
stale. **Redis is claimable.** Note KQ2 explicitly *declined* Redis ("it is an in-process
cache… no per-request Redis layer for this query") — that is a deliberate engineering choice
worth telling, not a contradiction.

**MySQL is historical, not banned.** The master résumé already carries *"Ported the data model
from Microsoft SQL Server to MySQL"* (Cura, 2015), and the journey doc corroborates it. Never
present MySQL as current or as deep expertise against a JD that demands it; in conversation,
frame PostgreSQL↔MySQL as transferable.

**Fixed facts:**

- **Rocket Software = "Software Engineer III" (IC)** who managed 5 engineers and their
  appraisals. **Never "Director", never "managing managers".** A people-management bullet
  there is honest; a title inflation is not.
- **Education = MS in Computer Science, University of Houston.** Never downgrade it. The
  IIIT postgraduate diploma in AI/ML coexists but is not the highest degree.
- **Java + Spring Boot are real and recent, across two employers** — Rocket (Aug 2018 –
  Jul 2019) and **Deque (Dec 2019 – Feb 2025)**. At Rocket, IBM Configuration Manager
  decomposed into Java/Spring Boot microservices. At Deque: the
  multi-tenant **axe Monitor** platform on **Spring Boot 2.x and Java 8/17**,
  customers consolidated onto shared instances, per-customer PostgreSQL on **Amazon
  Aurora**, every instance migrated from isolated **Keycloak** to central **Red Hat single
  sign-on** with zero user disruption, and **OpenID Connect + OAuth 2.0** flows configured.
  Java actually spans roughly **11 years across three eras**.
- **The VoltusWave VP role ended Apr 2026** — he is available immediately. Reason for
  change is the honest VoltusWave/Amura cashflow situation. Never invent a better one.
- **Current location is Hyderabad** (set 2026-08-25). This is where he lives now — distinct
  from the still-open question of whether the *Deque role* was Hyderabad or Bangalore, which
  the journey doc records unresolved. Location is **card-only**: it lives in Hiration's
  Personal Information modal with phone, email and LinkedIn, and the bot never writes it. It
  only edits `#personal_title_1`, the headline. **Relocation stays open** and is never a
  scoring constraint.
- **The VoltusWave org was 6 sub-teams** — backend, React Native, web, artificial
  intelligence, quality assurance (QA), DevOps. Never "5". He hired QA engineers.
- **Safe to claim:** Django, FastAPI, LangChain, LangGraph, real Model Context Protocol
  (MCP) servers, Deque role-based access control and US–India teams, least-privilege,
  React (web), a measured Claude Code / Codex rollout, Datadog. Metrics: hotel conversions
  **+65%**, ELK cost **−46%**, 8 early clients, and **25 hotel suppliers integrated through a
  MuleSoft enterprise service bus** — all four user-supplied and safe to claim.
- **Kubernetes and Terraform are CLAIMABLE — user-confirmed 2026-08-25.** He ran both,
  hands-on, at VoltusWave. **This rests on his word alone, and that is sufficient** — the rule is
  "journey doc **or** user-confirmed". Do not re-flag either. Consequence: Kubernetes is a hard
  requirement on several IC seats, and any score that docked it as an unrecoverable cap must be
  re-scored, not merely annotated.
  ✅ **Corroborated 2026-08-25 by a read-only card dump.** Both sit in bullet 10 of the **17
  VoltusWave bullets on `august_master_resume`** — *"Operationalised Amazon Web Services on
  **Kubernetes, Terraform**, Elastic Container Service Fargate at 70% Spot — deploy time under
  10 minutes, infrastructure cost down 25–30%"*. That single bullet also corroborates the two
  user-confirmed metrics below, and attaches them to the VoltusWave second stint.
- **⚠ TWO LIVE CARDS CARRY DIFFERENT VOLTUSWAVE BLOCKS — this caused a full session of confusion.**
  - `august_ic_master_resume` (the export default) — VoltusWave = **10 bullets, identical to
    `master/upgrad_resume.html`**. No Kubernetes, no Terraform, no Fargate, no k6.
  - `august_master_resume` (the older, leadership-flavoured card) — VoltusWave = **17 bullets**,
    and this is the block every handoff note meant. It carries Kubernetes, Terraform, ECS Fargate
    at 70% Spot, k6-validated load testing, React Native across 2 app stores, the four named
    archetypes, the `TraversalSource` wrapper and Rosenbaum γ + E-value.
  **Dumping only the IC card produced a confident, wrong conclusion that the 17 bullets did not
  exist. Dump BOTH cards before reasoning about what a card contains.**
  `automation/dump_card.py --card <name>` is read-only and writes
  `master/live_card_dump*.json` + `.md`. Both dumps are committed so this can never be lost again.
- **The Deque gap is real and separate.** Both cards carry **14 Deque bullets**;
  `master/upgrad_resume.html` carries **6**. Eight are unmerged, including Jenkins → GitHub Actions
  with ISO 27001, PostgreSQL → Amazon RDS, a Puppeteer regression framework, the axe-core
  spider/scanning pipeline, run-over-run regression comparison, and API versioning.
- **✅ HIGH-AVAILABILITY DESIGN IS REAL — user-confirmed 2026-08-25.** His words: *"GO Chat
  Service and the 2 Data Stream has HA design, multi AZ deployment, failover, disaster recovery,
  etc since we needed certification."* So HA attaches to the **Go chat service and the two-stream
  Kinesis design** — multi-availability-zone deployment, failover and disaster recovery — and the
  **driver was a certification requirement**. Claimable. It closes what the Yes Madam rubric had
  booked as an unrecoverable 2.0-point floor.
  ⚠ **Scope it correctly: this is the CHAT PLATFORM, not Amura.** The Amura corpus names no
  broker at all (see the Kafka/Kinesis guardrail above). Never let HA evidence migrate across.
  ✅ **SETTLED 2026-08-25: the certification is HIPAA.** He answered directly. Name it in the
  bullet; it no longer reads "a certification requirement". ⚠ Keep it distinct from Deque's
  *"achieving ISO 27001"* — different employer, different certification, and a reader can merge
  them. Be ready to say so out loud.
  ✅ **LOAD BALANCING IS HIS — user-confirmed 2026-08-25.** He owned the load-balancing layer.
  It is a *required* line on several JDs and previously scored zero because the re-score
  correctly refused to infer a balancer from multi-availability-zone plus failover. Claimable
  now. **Open: the specific shape** (Application vs Network Load Balancer, target groups, health
  checks) — do not guess a product into a bullet; "load balancing" alone is what he confirmed.
- **✅ TERRAFORM AND KUBERNETES WERE ADOPTED AS A COMPANY-WIDE STANDARD — user-confirmed
  2026-08-25**, not merely run by him. This is an *adoption* artefact, the same shape as bullet 8's
  Go and DynamoDB across five sub-teams, and it satisfies a "standards implemented and adopted,
  not just documented" criterion rather than only a "ran the tool" one.
- **✅ ALL 17 BULLETS USER-CONFIRMED ACCURATE, 2026-08-25** — his words: *"everything is
  accurate."* Do not re-flag any of them for factual accuracy, and do not scrub any of them.
  Two readings this settles:
  - **6 sub-teams vs 5 is NOT a contradiction.** Bullet 3's *"6 sub-teams"* is the whole
    VoltusWave org; bullet 8's *"5 sub-teams"* is how many adopted Go and DynamoDB. Both stand.
    The "never 5" rule above governs the **org size**, not adoption counts.
  - **ECS Fargate at 70% Spot, k6-validated load testing, React Native across 2 app stores with
    Firebase Cloud Messaging and Apple Push Notification service, the HIPAA framework, and the
    four named archetypes are all confirmed.** Earlier passes marked several "uncorroborated"
    because they are absent from the journey doc and case studies. **Absence from an incomplete
    record was never absence in production** — he was there. Do not re-flag.
- **⚠ The 17 bullets are NOT safe to paste wholesale.** Several state pre-registered acceptance
  **targets** as achieved results, which the honesty rules forbid: bullet 16's *"warm-path P99
  < 200 ms, NDCG@10 ≥ 0.75"*, bullet 17's Rosenbaum γ + E-value battery, and bullet 15's large
  language model narrative guardrails (KQ9's shared contract is unsigned and its narrator ships
  **off by default**). Bullet 5 carries the **"500 → 100,000 concurrent users"** wording the Status
  section already flags as overstating a burst test. Merge selectively, per-claim, never as a block.
- **User-confirmed 2026-08-25, safe to claim: infrastructure cost cut 25–30%, and deploy time
  from hours to under 10 minutes.** Neither appears in `professional-journey.md` or the
  original — an earlier pass flagged them as unsourced and he corrected it. The rule is
  "journey doc **or** user-confirmed", not journey-doc-only; he was there and the record is
  incomplete, not the claim. **Do not re-flag these.** Open only: which role they attach to —
  his live card places them beside the VoltusWave second stint.

**Open claims — HE settles these, not us.** Never rewrite them in either direction on your own
initiative; surface them in every technical-round prep artefact and leave the résumé wording
alone until he decides. The journey doc *asks* several of these questions, so it cannot resolve
them for you.

- ~~The graph neural network~~ — **SETTLED 2026-08-25: he confirmed it is real and it is in the
  headline.** It attaches to the Context Graph, which the ten killer-query case studies do not
  document — absence there was never absence in production. **Prep consequence:** it is now in
  word-position four of his headline, so "walk me through the graph neural network architecture"
  is a certainty in any technical round.
- The **27 ms / P95 16 ms** pairing — P95 below mean is a strength *if he names the tail*.
- Whether the **large language model narrative guardrails** actually shipped.
- **"hand-coded"** vs **"spearheaded"**.
- **"500 → 100,000 concurrent users"** — overstates a burst test: one request per user, no
  sustained load, no 500 baseline.
- **The four Rocket metrics** — 5-engineer team, bugs −50%, adoption +20%, sales +20%. The
  journey doc records these as *"from the résumé… confirm each"* and lists confirm-or-reject as
  a blocking question. The Java/Spring Boot **decomposition** itself is confirmed in his own
  words; only the numbers are open.
- **Deque's 70–80% consolidation** figure, and whether ~300 refers to customers or instances.

⚠ These are **confirm-or-reject** items, not fabrications to scrub. Several already sit on the
master PDF and have gone out in submitted applications.

**Do NOT retroactively remove a claim that has already gone out.** Reaffirmed by him 2026-08-25.
Removing it does not unsend it — it only creates a gap between the version a recruiter holds and
the version they would see next, which is worse than the original ambiguity. The work is being
**ready to answer for it in a room**, not editing the file. Surface it in prep; leave the résumé
wording alone.

**The one exception — UNVERIFIED is not the same as FALSE.**

- **Unverified** — absent from the record, but he may well remember it. The +65%, the Rocket
  metrics, ~300 instances, 70–80%. These **stay** on the résumé. Flag them for prep, never scrub.
- **False** — contradicted by a source we hold. These come off regardless of whether they have
  been submitted, because the contradiction is what an interviewer will find. The RAG bullet
  claiming retrieval ran over an Amazon Neptune context graph was this: KQ1's own stack table
  names Elasticsearch the authoritative serving index and puts Neptune deliberately off the
  serving path. That was corrected on 2026-08-25 — the only such correction to date.

Before proposing any removal, say which of the two it is. If you cannot, it is unverified, and it
stays.

**Client names stay off written artefacts.** Spoken, the regulated-bank customers are
load-bearing evidence for the isolation work — do not strip them from spoken prep.

---

## Résumé hygiene — every bullet satisfies ALL

Canonical reference: `resume-issues-to-avoid/`.

- **≤25 words**
- **Strong action-verb opener** — never `Managed` / `Replaced` / `Responsible for` /
  `Worked on` / `Helped`
- **Leading verb unique across the résumé** — same-root variants collide
  (`Architected` ≈ `Architecting`)
- **≥1 number, %, scale marker, or measurable outcome**
- **≥1 bolded fact** in the paste source
- **No trailing period**
- **Every acronym expanded on first use**, in reading order

Common expansions: AI, GNN, AWS, ECS, RDS, ELK (Elasticsearch/Logstash/Kibana),
RHEL (Red Hat Enterprise Linux), QA (Quality Assurance), REST, SaaS, HIPAA, ISO, CEO, VP,
NMT, MCP (Model Context Protocol), SSO (single sign-on). **Tagline exception:** the headline
may keep common acronyms unexpanded (SaaS, AI, ISO 27001); the summary immediately after must
expand them on first use.

**Expand every acronym and unfamiliar domain term on first use EVERYWHERE** — not just résumé
bullets, but `research.html`, dashboards, call cheat-sheets and chat replies. For a domain he
has not worked in, put a plain-English glossary at the top of `research.html` that defines the
*concept*, not merely the expansion. Call out misleading collisions: SOC 2 the audit standard
versus a SOC, the security operations centre.

### Verb pool

*Rebuilt 2026-08-25 from `master/upgrad_resume.html` — this list is now real, not inherited.*

- **Used — do not reuse as leading verbs** (all 27 leading verbs in the master, regenerated
  2026-08-25 after the Amura additions): Architected, Scaled, Deployed, Delivered, Engineered,
  Drove, **Hardened, Extracted, Sequenced, Secured**, Implemented, Steered, Forged, Productized,
  Stewarded, Championed, Anchored, Coached, Surfaced, Partnered, Co-founded, Mobilized, Helmed,
  Codified, Cut, Reconciled, Lifted.
- **ATS power verbs — current role ONLY — still free:** Secured, Optimized, Strengthened,
  Built, Spearheaded, Improved, Increased. *(Established, Launched, Designed, Reduced and
  Owned are burnt — their roots appear mid-bullet as establishing / launched / design /
  reducing / ownership.)*
- **⚠ THIS LIST WAS STALE AND IS CORRECTED 2026-08-25.** Verified directly against
  `master/upgrad_resume.html`: **Translated, Calibrated, Replatformed, Piloted, Eliminated,
  Bridged, Curated, Seeded and Salvaged each already lead a bullet.** All nine were documented
  as free and none was. **Never trust this list — regenerate it from the file.**
- **Verified free against the master, 2026-08-25:** Instrumented, Brokered, Halved, Trimmed,
  Increased, Improved, Unified, Partitioned, Released, Staged, Wired, Sustained, Scoped,
  Specified. *(`Built` is NOT free — `Build`-versus-buy sits mid-bullet in the skills block.
  `Tuned` looks taken by `Neptune` but that is a substring, not a shared root.)*
- ~~**Fresh verbs — older roles only — still free: Translated, Calibrated. That is all.**~~
  Thirteen of the original fifteen went into the master.
- **Verified free against the master, for Rule 7 top-ups:** Instrumented, Replatformed,
  Brokered, Piloted, Eliminated, Halved, Bridged, Curated, Seeded, Salvaged, Trimmed.
  *(Extracted, Hardened, Sequenced and Secured moved to the used list on 2026-08-25.
  `Built` is NOT free — `Build`-versus-buy sits mid-bullet in the skills block.)*

**Check uniqueness across ALL TEN roles, not just the five parsed ones.** The card-only
pre-2016 roles (§§11–15) live in the same file and their leading verbs count. Missing that
on 2026-08-25 put `Hardened` in both VoltusWave and El Paso, and `Extracted` in both
VoltusWave and CURA.

**Same-root collisions count, and they hide mid-bullet.** Check the whole master, not just the
leading words: `Lifted` as a leading verb sat alongside *lifting sales* and *lifting revenue*
until 2026-08-25. **Regenerate after every master edit** — extract the leading word of each
experience `<li>`, then grep each candidate's stem across the entire file.

### Rule 7 — re-vector experience bullets per job, always

Back each surfaced skill with bullet-level evidence across the **current role + 2–3
prior**. Edit **in place, keeping the leading verb**; only add a new bullet with a verb
confirmed free. Real work only.

Top-of-résumé-only tailoring produced **zero calls in June 2026**, the window when tailoring
had drifted top-of-résumé-only; per-job bullets produced the calls. One honest confounder: two
June applications also went out under-tailored for delivery reasons, so method and delivery
moved together. The rule is a direct user directive and stands regardless.

---

## JD match scoring — two scores

**(1) TECHNICAL — target 95+. This is the score he cares about**, and getting it close to a
95% match is the job. Score it with **subagents, one per rubric criterion** (see *Execution
model*). Engineering capability. Read "e.g. / or / preferably"
qualifiers generously: Python satisfies "e.g. Python, C++, or Rust"; LangChain satisfies
"e.g. LangChain, LlamaIndex". A specific named tool he has not used (MongoDB vs his
DynamoDB, OpenTelemetry vs his Datadog) is a **ramp item, not a capability cap**. Honesty
caps the score only when a genuinely CORE required technology is absent — a true must, not
an "e.g." Never fabricate to force 95.

**(2) NON-TECHNICAL / FUNCTIONAL — informational, never a gate.** Industry domain,
commercial context, representation. It must not block applying and must not drag the
technical score.

A weighted rubric (criterion, weight, /10, evidence) backs the technical score. Name the
binding constraint and the smallest lift. **Real-world gates — compensation, levelling,
legitimacy — are named separately from both scores.**

**⛔ COMPENSATION IS DEFERRED — set by him 2026-08-25.** His words: *"forget about
compensation… it'll come up when we hear back and get to that stage."* Same shape as the
interview-prep rule: the trigger is **a company responding and the conversation actually reaching
that stage**, not a score, not a workspace being built, not a JD listing a band.

Until then: **do not research it, do not surface it, do not gate on it, do not name it as a
red flag, and never let it drag a score.** A listing whose band looks low is not a reservation
worth writing down. Do not compare any band to any floor in a workspace artefact. If a JD states a
band, record it as a neutral fact in `jd.md` and stop there.

**When it does arrive** — a recruiter asks, or a process reaches that stage — the figures below
are his standing answer. They are kept here for that moment, not for analysis:

**Compensation (for when it comes up, not before):** current **₹72L**, expected **₹75L–₹1Cr**. The ₹75L floor is a ~4% step,
not a stretch; a band topping out under ₹72L is a pay cut. Midpoint ₹87.5L if one figure
is required. **Current CTC ₹72L is sensitive, but the absolute ended 2026-08-11 — he decides, not the
rule.** Default: never volunteer it unprompted and never put it in a draft on your own
initiative. **When he says disclose it, disclose without re-litigating.** Name the trade once —
₹72L against a ₹75L floor is a ~4% ask that reads as considered, but it anchors the band near
₹72–75L and takes the ₹1Cr end off the table — then proceed, and stage a follow-up line for
when the counter anchors to the current figure.

Apply **broadly**. Surface reservations in the workspace and let him decide. Honesty
governs résumé *content*, never whether to apply.

---

## Voice

Drafted prose — application answers, LinkedIn messages, cover notes — must read human.
Avoid aphoristic closers, "three loops" framings, em-dash overuse, and the words
"non-negotiable", "blast radius", "compounds over a career".

**Outward-facing pieces lead with strengths and never proactively flag his gaps.** Honesty
means not claiming what is false, not advertising what he lacks. Internal dashboards still
name gaps plainly.

**Anything he will paste** — outreach, application answers — is staged as copy/paste HTML
with a working copy button (`data-copy-target="#id" data-copy-html="1"`, which preserves
bold), not as chat text.

**Recruiter replies: answer exactly what was asked, in the order asked, then put a call on the
table.** No added questions of your own, however useful they look — every extra question is one
more thing standing between him and a phone call. Lead with **available immediately, nothing to
serve**. Include **+91 93640 27487** whenever the reply invites a call. **When expected
compensation is asked, give ₹75L–₹1Cr fixed** (midpoint ₹87.5L if one figure is required) and
anchor it to the seat's level rather than to him. Everything else goes to the call cheat-sheet
and gets asked out loud. When proposing a call time, offer a slot **~2 days out, never
tomorrow** — the gap is where his read forms.

---

## Layout & automation

- Workspaces: `Month-YYYY/DD/<slug>/` → repo root is `../../../`. Raw inputs:
  `job-applications/Month-YYYY/DD/`.
- **No per-file `<style>` blocks.** Shared classes live in `style.css`.

### The launcher renders from the database

`index.html`'s Applications list comes from `jobs_tracker_v2` via `GET /api/jobs`, not from
markup. **Never hand-write a row into `#app-list`** — a row added by hand is a row no query
can see, which is exactly how the page came to show 4 applications while the database held 92.

- **One row per slug, grouped by intake date**, in v1's shape (set by him 2026-08-26 against
  v1's launcher): underlined text tabs with count badges, a right-aligned search box, a
  `COMPANY · TITLE · TECH · NON-TECH` strip per group, and an expandable detail row.
- **v1 AND v2 ARE SEPARATE DATABASES — set by him 2026-08-26.** His words: *"let's use a
  different database? like `jobs_tracker_v2`? this way we DO NOT interfere with v1 jobs?"*
  `jobs_tracker` is v1's record — **92 seats, frozen, nothing in v2 opens it**.
  `jobs_tracker_v2` holds v2's seats and only v2's seats. **All SQL lives in `db/`**:
  `db/migrations/` (004 creates the database, 005 moves the seats, 006 reverses the archive),
  `db/schema.sql` for `v2_daily`, and `db/README.md` explaining which applies to which.
  Verify all three databases read-only with `psql -d postgres -f db/verify.sql`.
- `automation/jobs_db.py` — read-only queries (`JOBS_TRACKER_DSN`, default `dbname=jobs_tracker_v2`).
- `automation/jobs_sync.py` — registers a seat, and re-reads every workspace's `score.json` to
  refresh its technical score. Idempotent; re-run it after any re-scoring.
- **Six tabs over eleven statuses, and deliberately no `all`** — `Ready to apply · Applied ·
  No longer available · Heard back · Not selected · Other`. That is v1's tab set exactly. The
  mapping and the two-score derivation are documented in `automation/README.md`.
  `recommended_skip` → **Other** is deliberate: those rows must not drag on the ready-and-unsent
  backlog gate.
- **⛔ THERE IS NO `archived` TAB AND NO ARCHIVE CONCEPT.** There was one, for a day —
  `db/migrations/003` archived v1's 92 rows in place. `db/migrations/006` reversed it when the
  separate database replaced it. A row that must be filtered out of every view is a row in the
  wrong database. `archived` is not in `TAB_FOR_STATUS`, not in `TABS`, and not in
  `jobs_tracker_v2`'s enum. **Do not re-run 003.** (The one thing 006 could not undo: PostgreSQL
  has no `DROP VALUE`, so `archived` remains in `jobs_tracker`'s enum, on zero rows, inert.)
- **A v1-rubric row's scores read `v1`, not a number.** They come off v1's five-axis triage
  rubric; `technical 20` beside `technical 88.4` invites a ranking that does not exist. No such
  row is served any more, but the rendering stays: `jobs_sync.py` still refuses to overwrite a
  five-axis breakdown, so the two rubrics can never be silently merged.
- **Intake-date group headers say `<date> — N seats` and nothing more.** Any clause after that
  is hand-authored in `automation/intake_notes.json`, which ships empty. The date and the count
  are derived; a sentence characterising a group of seats is not, and is never composed.
- ⛔ `applications.salary` is never selected or rendered — compensation is deferred.
- Served by plain `http.server` there is no API, and the page **says the list is unavailable**
  rather than rendering an empty grid.
- **Counts are derived from the rows in the DOM**, and `static/tabs.js` re-derives them from a
  `MutationObserver` on `#app-list`. Counting only on `DOMContentLoaded` showed every tab
  reading 0 above a full list, because the rows arrive from `/api/jobs` long afterwards.

### Capture the history — `application_events`

**Set by him 2026-08-26: *"we should capture our history properly."*** `status_events` records that
a row moved `resume_drafted → applied`. It cannot record that a recruiter sent an InMail, that he
replied, that two job descriptions came back four hours later, or that a CV was requested. Those
are what a process is actually made of, and they are what **v1 never had** — one process ended in an
unexplained rejection with no recording, another produced no debrief at all.

`db/migrations/009_application_events.sql` creates the timeline. Six kinds: `inbound` · `outbound` ·
`document` · `call` · `status` · `note`.

- **`actor` is REQUIRED.** *"Someone sent a JD"* is the shape of a record you cannot use later.
  A named human for their side, `Abhisheik` for his.
- **`detail` holds the message VERBATIM** where one exists. A paraphrase six weeks later is not
  evidence of what was said. Paul Abbott's two messages and Harisri Parthasarathi's InMail are
  stored in full.
- **`artefact`** is the repo-relative path when a file changed hands — a JD PDF, an exported résumé.
- Append-only in spirit: **correct by adding an event, never by editing one.**

```
psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
     set_config('ev.slug','<slug>',false), set_config('ev.kind','inbound',false),
     set_config('ev.actor','<who>',false), set_config('ev.summary','<one line>',false),
     set_config('ev.detail','<verbatim>',false), set_config('ev.at','<ISO ts>',false)" \
  -f db/operations/log_event.sql
```

**Log an event every time something happens** — an InMail arrives, a reply goes out, a document
changes hands, a call is scheduled or held. The cost is one command; the cost of not having it is
the v1 lesson.

### The daily log

`daily/index.html` — what is due, what is blocked, what is next. **Generated, never authored:**
`daily/days.json` is the source and `automation/daily.py` owns the markup.

```
automation/.venv/bin/python automation/serve.py     # replaces `python3 -m http.server 8006`
automation/.venv/bin/python automation/daily.py     # regenerate the page from days.json
./todo                                              # what's due, from the terminal
./todo backlog                                      # what's moved out, and what can come back
```

- **State lives in PostgreSQL** (`v2_daily`), not in the HTML and not in the browser.
  `task_state` is what the page renders; `task_event` is append-only history — every tick,
  park, push and drop with its reasons and timestamp. Schema: `db/schema.sql`;
  migrations in `db/migrations/`. **All SQL in this repo lives in `db/`** — set by him
  2026-08-26, so every schema and data change is re-runnable and verifiable later.
- **`serve.py`, not `http.server`.** Same port 8006 so a pinned tab keeps working. It adds the
  state API, sends `no-store` so a refresh really refreshes, and binds `127.0.0.1` because it
  writes to a database. Against plain `http.server` the page falls back to localStorage and
  says so in the banner.
- **Each task carries a priority and dependencies.** A task whose prerequisites are unticked is
  marked *waiting* but never disabled — doing things out of order is legitimate.
- **Unfinished tasks roll over automatically.** Never duplicate a task in `days.json` to carry
  it forward.
- **Moving a task out always needs at least one reason**, and reasons decide whether it can
  come back: a task is revivable only if **every** reason it carries is revivable
  (`revivable` in `days.json`). One terminal reason — the posting is gone — closes it.
  The CLI refuses to move a task out with no reason and no terminal to ask on, rather than
  inventing one. That refusal is deliberate: an agent has to come back and ask.
- Tests: `bash automation/tests/run.sh` (the page suite needs `npm install jsdom`).

### Making a résumé, and its paste sheet

```
automation/.venv/bin/python automation/resume.py new   --slug <slug> [--company X --role Y]
automation/.venv/bin/python automation/resume.py sheet [--slug <slug>] [--since <git-ref>]
```

- **`new`** scaffolds a whole job workspace: the dated directory, `upgrad_resume.html` copied
  from the master, an empty `paste_notes.json`, a `jd.md` to paste into, a per-workspace favicon,
  and a row in `jobs_tracker_v2` as `resume_drafted`, which the launcher shows under *building*.
  Everything repeated 15–20 times a night.
- **`sheet`** emits `<workspace>/paste_sheet.html` — every section as ONE copy block, generated
  **from** the résumé so it cannot disagree with what the bot writes. Which sections changed is
  derived by diffing against git; `--since <ref>` is needed when the change is already committed,
  because diffing a committed file against HEAD correctly reports nothing changed.
- The *reason* a section changed cannot be derived — it comes from `paste_notes.json`
  (`{"quick-summary": {"why": …, "heads_up": …, "hygiene": …}}`). A changed section with no note
  says so rather than inventing one.
- `automation/add_breadcrumbs.py` and `automation/expand_acronyms.py` — both idempotent, both
  safe to re-run when new pages land.

### Case studies — VoltusWave · Amura

`killer-query-case-studies/` is **v1**, complete and committed (46227bd). Ten killer-query case
studies plus Q&A companions, ~198,000 words: what was implemented for Amura, a chronic-care
platform covering 80+ conditions.

**Everything in v1 SHIPPED — he confirmed it 2026-08-25.** Do not let an extraction downgrade
it. The documents say *"the contract was signed and the query is live"*; what several pages
record as *"approval pending"* is an internal **design-review sign-off**, not deployment
status. Shipped and approved are different things and the source keeps them apart correctly —
a first extraction pass misread the governance state as delivery state and under-claimed.

**⚠ He does NOT have the outcome numbers. He left VoltusWave before he could capture them.**
So Amura bullets carry **design and scale markers**, never impact metrics: 80+ conditions,
a 6-hour cache TTL, a 90-day outcome-maturity window, twenty adversarial-review findings
absorbed into a hardened v2, 13 of 13 local findings closed. Those are facts from his own
documents. **Add one more, user-supplied and safe to claim: the platform held 9–10 years of
patient history**, which is why any killer query needing historical data could actually be
answered. That figure is load-bearing rather than decorative — as-of featurisation,
leakage-safe labelling, 90-day outcome maturity and sequence mining are only meaningful with
years of longitudinal data behind them, so it is the number that makes the rest credible.

**⚠ THE SINGLE WORST HONESTY LANDMINE IN THE CORPUS — KQ2's illustrative served-cell table.**
`kq2-outcome-correlation.html` prints `Metformin + concurrent nutrition | 412 | 0.58 |
[0.53, 0.63]` against `Metformin alone | 217 | 0.34 | [0.28, 0.41]`, a `+24 percentage points`
difference and `max SMD 0.08` across eight covariates. It is formatted exactly like a measured
result. The page labels it in its own words: *"**Illustrative response shape, not a production
measurement.**"* The prep page instructs saying the word aloud. **None of 412, 217, 0.58, 0.34,
+24pp or 0.08 may ever appear on a résumé or in a room as an outcome.** Same class: KQ1's
*"300 patients in India on protocol A"* is an illustrative example, not a cohort size. Of
198,000 words this is the block most likely to be mistaken for the impact metrics he does not
have. Verified directly 2026-08-25.

**⚠ Amura names NO message broker — verified 2026-08-25: `Kafka` 0 hits and `Kinesis` 0 hits
across the entire corpus.** The source deliberately says only *"its streaming transport"*. **The
master's Kinesis bullet is the CHAT PLATFORM, a different system.** Keep them apart, and never
cite Amura as Kinesis evidence. (Kinesis remains confirmed in production for the chat platform.)

**The 6-hour cache TTL belongs to KQ4, not KQ1.** Verified 2026-08-25: `kq1-precedent-search.html`
is **TTL 1h**; `kq4-early-signal-detection.html` is **TTL 6h**. Both are safe markers — attach
each to the right query. `TraversalSource` is corroborated **in substance but not by that name**;
KQ9 words it *"tenant-scoped traversal-source wrapper"*, which is how to write it.

**Latency achieved, adoption, error reduction, cost saved — he cannot supply these,
so they are `[fill in metric]` or absent. Never invent one, and never ask him again for a
number he has already said he does not have.**

**Do NOT wait for v2. Finish everything on v1.** Bullets, workspaces, prep artefacts — all of it
gets built from v1 now. v2 needs a few more points and is **days-to-weeks away**; holding work
back for it is the build-instead-of-send failure wearing a different hat.

When v2 lands it goes in `killer-query-case-studies-v2/` — **never overwrite v1 in place.**
`professional-journey-original.md` line 231 and the launcher link both point at v1 and stay
valid, and keeping both side by side is what makes the diff possible. At that point: extract v2,
diff it against v1, and revise only what actually moved.

**The v1↔v2 diff is honesty work, not bookkeeping.** A claim that moves from *shipped* to
*designed* between his own two versions must never reach a résumé as shipped. Extract both,
diff them, and treat any downgrade as binding.

**Status vocabulary, preserved from the source and never upgraded:** `shipped-production` ·
`shipped-ci-only` · `designed-reviewed` · `designed-only` · `unclear`. The material draws this
line itself — *"components landing does not by itself convert a review verdict"* is its own
wording. Anything derived from it inherits that precision.

> ## ⛔ SUPERSEDED 2026-08-27 — the seven sections below describe a pipeline we have LEFT
>
> **Set by him: we are moving off the upGrad / Hiration résumé builder. Résumé layout and PDF
> export are done by hand in Canva Pro from now on, and the upGrad login/export step has been
> removed from the automation workflow.**
>
> Everything from here to *Naukri quirk* — **upGrad export · Which master card · Card deletion ·
> Copy blocks · Pasting into Hiration · Editing the card itself · upGrad paste quirk** — is kept
> as history, not as instruction. Do not run it, do not re-add it to `daily/days.json`, and do not
> plan work around it.
>
> **The files stay. He said so explicitly: "do not remove the files. just remove the step from the
> automation workflow."** All nine scripts remain on disk — `upgrad_apply.py`, `upgrad_login.py`,
> `upgrad_creds.py`, `upgrad_resume_paste.py`, `browser.py`, `cleanup_cards.py`,
> `fix_master_card.py`, `dump_card.py`, `update_master_card.py` — along with both Hiration cards
> and the encrypted credentials. Legacy, not garbage. **`cleanup_cards.py` is still never run.**
>
> **What changes in practice:**
> - `master/upgrad_resume.html` is now the **complete content source**, not a ten-section paste
>   feed. It already carries everything the card used to own: the dates table for all ten roles,
>   Education, Certifications, and Personal Information (Hyderabad · +91 93640 27487 ·
>   abhisheik@abhideo.ai · LinkedIn `abhisheikdeo`). Nothing is trapped in Hiration.
> - The **paste matrix is moot.** `<p>`-versus-`<ul>` and the synthetic `ClipboardEvent` existed
>   solely to force bold and bullets through Draft.js. Canva has no such constraint.
> - There is **no ATS "Resume Review" score** any more. CLAUDE.md already said not to chase it.
> - **`verify-pdf` is now the only gate.** Nothing upstream enforces dates, bold, the LinkedIn slug
>   or the 3-page cap — a hand-built PDF can drift in ways no script catches.
>
> **Two ATS risks specific to Canva, worth stating once:** most Canva résumé templates are
> two-column with icons, and a multi-column PDF is the classic parsing failure — the reader
> interleaves bullets across columns. Single column, real text boxes, nothing baked into shapes.
> And `resume-issues-to-avoid/` rule 9 is exactly the bold-stripped-on-export failure; verify bold
> on the exported file, not in the editor.
>
> Still open, his call: whether the per-workspace `bullets_for_upgrad.html` artefact and the
> `upgrad_resume.html` filename should be renamed now that nothing pastes into upGrad.


### upGrad export

```
UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py \
    --slug <slug> --no-pause --reset
```

Run from the repo root. It clones a master Hiration card, overwrites **the ten parsed
sections** — headline, summary, three skills blocks, five experience roles — from the
workspace's `upgrad_resume.html`, exports `<workspace>/Abhisheik_Deo_Resume.pdf`, and
prints ATS JSON. The persistent browser profile (`.playwright-profile/`) sits at the repo
root, so **cwd matters**. Login is automated from encrypted credentials in `automation/`
— gitignored, **never commit them**. The bot runs serially (shared browser).

### Which master card

Two live masters, both in `cleanup_cards.py`'s `PROTECTED` set:

- **`august_ic_master_resume`** — the IC card. **Created by cloning `august_master_resume`,
  not from blank.** That base already carries all ten experience entries — the five the bot
  writes plus the five pre-2016 roles it never touches — along with dates, education and
  certifications. So building the IC card is **overwriting text in an existing skeleton**, not
  creating sections. Content comes from `master/upgrad_resume.html`. It is the **script
  default** as of 2026-08-25 — a bare export uses it, no flag needed.
  **The name is not finalised.** Until a card exists in Hiration under exactly this name,
  every export fails loudly at `stage_find_master` with a "check the card name, or pass
  `--master`" message. That loud failure is intended; the previous silent fallback to the
  other card was the bug. Renaming means one line in `upgrad_apply.py`, one in
  `cleanup_cards.py`'s `PROTECTED`, and this block.
- **`august_master_resume`** — kept deliberately; it may still be used for future positions,
  and it is the base the IC card is cloned from. No longer the default: reach it explicitly
  with `--master august_master_resume`.

### ⛔ Card deletion — ask first, every time

**Never run `cleanup_cards.py` at all until he explicitly says to delete a specific card.**
Not after an export, not after a submission, not as tidy-up. He asks, by name, or it does not
run. A bare, slug-less run deletes every temp card; even `--slug <slug>` is his call to make,
not a follow-up to infer. Tailored `<slug>_ats_resume` cards accumulating is the intended
state, not a mess to clean.

**⚠ Dates live in the Hiration card, not the HTML.** The bot overwrites bullet text only, so
the card itself must already read Apr 2026. On `august_master_resume` it already does
(VoltusWave 2025-03-01 → 2026-04-01, Deque 2019-12-01 → 2025-02-01) — **verify after cloning
rather than assuming a clone preserved them.**

**Education, certifications and the pre-2016 roles are card-only** — the bot never touches
them. They already exist on the card, carried over from v1, so the work is correcting their
text by hand in the Hiration UI. **The one that matters is El Paso**: it is a Java role —
Senior Java Developer, JSP and Java Enterprise Edition, Tennessee Gas Pipeline — and the v1
card describes it as .NET, hiding four of the eleven Java years.

**Verify every exported PDF:** dates correct (VoltusWave ended **Apr 2026**), bold renders
heavier, content matches `bullets_for_upgrad.html`, contact details and the LinkedIn slug
**`abhisheikdeo`** (not `abhideo` — that is the email domain), no `[fill in metric]`, and
**≤3 pages**. The ATS "Resume Review" score wobbles 87–99 on hygiene, not JD
fit — don't chase it. (No print dialog is involved: the bot exports headlessly and
`html_to_pdf.py` uses Playwright's own PDF call. If a résumé PDF ever comes from a source
document instead, export it from that application rather than via the browser's Print to PDF,
which flattens bold.)

`automation/html_to_pdf.py` renders any workspace HTML to PDF via headless Chromium.

### Copy blocks — one whole section, always

**A copy block is one complete section that REPLACES its counterpart wholesale. Never a fragment
to merge into an existing block.** Set 2026-08-25, and it holds for the master résumé and for
every per-job résumé.

- One button, one section, one paste. He selects the section in Hiration, deletes it, pastes.
- **Never** "add this line to Engineering Excellence" or "paste these two bullets under the third
  one". A partial paste means reading the existing block, working out where the new text goes, and
  not duplicating what is already there — three chances to get it wrong, silently, in a field he
  cannot easily diff afterwards.
- If a section changed by one word, the block still carries the **whole** section.
- **Key Skills is one section, not three.** It renders as three sub-groups —
  Technology Leadership & Strategy, Engineering Excellence, Business & Delivery — but when
  tailoring per job it is **replaced whole**, all three groups at once. The paste sheet carries a
  combined block for exactly this. Set by him 2026-08-25.
- **His skills format is short capability labels, not sentences** — `Multi-Tenant SaaS
  Architecture (Shared-Schema, Per-Tenant Isolation, Regulated Carve-Outs)`, never a descriptive
  clause. It scans; prose does not. Match it.
- **Generate copy blocks FROM the résumé file, never retype them.** A paste sheet that disagrees
  with the file the bot writes from is the drift that merging three files into one removed.
- Content that did not make it into a section is **not offered for pasting at all** — record it as
  considered-and-not-applied, with no copy affordance, so nothing loose invites a hand-paste.
- `data-copy-html="1"` on every button. A hand-dragged selection loses bold, and that does not
  surface until the exported PDF.

### Pasting into Hiration — the matrix, settled 2026-08-25

**No markup gives both bold and bullets through a real clipboard paste.** Tested by him, all
three cases:

| shape | bold | bullets |
|---|---|---|
| `<p>` per line, pasted alone | ✅ | ❌ |
| several `<p>` at once | ✅ | ❌ collapses to one line |
| `<ul><li>` compact | ❌ | ✅ |

His console output proved the clipboard itself is correct — 18 `<strong>` tags, `ClipboardItem`
present, rich path taken. **Hiration strips it on the way in.** Whitespace between tags was ruled
out too. Do not go looking for a fourth markup shape; the space is mapped.

**THE EXPORTER IS THE PATH.** `_paste_html` in `upgrad_apply.py` dispatches a *synthetic*
`ClipboardEvent` carrying `text/html` straight into Draft.js, which honours `<ul>`, `<li>` and
`<strong>` natively. That is where v1's "100% formatting carried over" actually came from — the
bot, never hand-pasting. A page on `localhost` cannot do this to an iframe on `upgrad.com`;
only Playwright can.

**So the ten parsed sections never need pasting by hand.** The exporter overwrites every one of
them from `<workspace>/upgrad_resume.html` on each run. The paste sheet is for *reading* what the
bot will write, and for one-off single-line fixes where `<p>` alone works.

**⚠ The upGrad onboarding modal blocks everything.** "Let's kickstart your career journey" renders
in the **top-level page** and overlays the iframe, so every click fails with *"subtree intercepts
pointer events"*. `_dismiss_modals` sweeps **every frame** — clearing only the app frame finds
zero, which is the trap. `stage_nav` retries the click once after clearing.

### Editing the card itself

`automation/fix_master_card.py` edits the **card-only** material the exporter never touches — the
five pre-2016 roles. Title and company are contenteditable divs with stable ids
(`PR_designation_N`, `PR_company_N`); bullets are a Draft.js editor inside `#PR-child-N`. It
refuses to touch a role whose current title is not what it expects, so it cannot silently rewrite
the wrong entry.

**Known limit:** bullet rewrites on the pre-2016 roles show in the editor and then **do not
survive the save**. The title does. Those three El Paso bullets are his to paste by hand.

### upGrad paste quirk

upGrad keeps raw `<strong>` but **strips styled `<span>`s, and strips bold from
list-rooted content**. So `bullets_for_upgrad.html` restates each changed bullet as a
standalone `<p>` with raw `<strong>` — never inside a `<ul>`.

### Naukri quirk

Naukri's "Job profile" textarea rejects `<` and `\`. Substitute: `<` → `under` / `below`,
`≤` → `within` / `at most`, `≥` → `at X+` / `above`.

---

## Intake flow — he pastes, we build

**Set 2026-08-25, by him, after a sourcing run he had not asked for.**

1. **He pastes the details** — job description, URL, screenshots, recruiter message, whatever
   he has.
   **⛔ ALWAYS ASK FOR THE URL — set by him 2026-08-26.** If he pastes a job description without a
   link, ask for it before building. A workspace whose posting cannot be reopened cannot be
   re-checked, and postings change, close and get re-listed under new requisition numbers. The URL
   goes at the top of `jd.md` and into `applications.source_url`.
   **`resume.py new` now REFUSES without one**: pass `--url <posting URL>`, or `--no-url "<reason>"`
   when the seat genuinely has none — an inbound recruiter InMail has no public listing, and that is
   a different fact from a URL nobody captured. The same shape as `./todo` refusing to move a task
   out with no reason: the tool comes back and asks rather than inventing.
   ⚠ **Never write prose into `source_url`.** The launcher reads that column as an `href`, so
   `"(no URL supplied)"` rendered as a broken link that looked real. It is a URL or it is NULL —
   `db/migrations/007` made the column nullable for exactly this, and both `resume.py` and
   `jobs_sync.register()` were manufacturing prose until 2026-08-26.
2. **We build the workspace** from that. Every pasted JD gets the full build, no re-asking.
3. **The database is the search layer.** He queries it; directories are storage, not an index.

**Do not source seats.** Not from job boards, not from company career pages, not "to have
something to apply to". A run on 2026-08-25 produced eight scored seats and he replied that
they were no longer valid. Sourcing spends real time producing a list only he can validate.
**Wait for the paste.**

**Do not re-rank or recommend an order** unless he asks. Auditing agent output against the
journey doc is required and stays required — report what the check found as a *finding*. Then
stop. Adjudicating a claim is not the same as ranking his options for him.

**OPEN — his call, not settled:** workspace layout. He floated "perhaps a single directory"
instead of `Month-YYYY/DD/<slug>/`, on the reasoning that the database handles search. Treat
the dated layout as current until he decides; `_resolve_slug_dir` in `upgrad_apply.py` already
supports a **root-level `<repo>/<slug>/`** workspace, so a flat layout would work today with
no code change.

## Execution model — workflows and subagents do the work

**If it CAN be offloaded to a subagent or workflow, it IS.** Set by him 2026-08-25 and it is the
default, not a preference — research, résumé drafting, JD scoring, workspace artefacts, extraction,
audits, drafting of any kind. Read each phase's results before choosing the next phase.

**The reason is to keep the main session FREE.** His words, 2026-08-25. Work that runs in the
main thread blocks it: he cannot paste the next job description, redirect, or ask something else
while it grinds. Work that runs in a subagent runs in the background and the session stays
answerable. With ~20 workspaces in a night, availability matters more than any single artefact.

**The test is not "is this hard enough to delegate" — it is "does this have to be me".** Almost
nothing does. When it feels faster to write it myself than to brief an agent, that is precisely
the instinct that blocks the session for the next twenty minutes.

**What genuinely has to stay in the main thread:**

- **Adjudicating** what comes back, and the **adversarial verify pass** against
  `professional-journey.md` — delegation is only safe because this happens.
- **His decisions** — the confirm-or-reject list, what to send, what to trim.
- **Coordination** — deciding the next phase, and status changes through `./todo`.
- Conversational turns, and running a command that already exists.

Everything else goes wide.

**Research a job → workflow.** A multi-modal sweep, one agent per angle: the company's own
site, comp signals, the seat's legitimacy and whether it is even open, red and green flags,
forcing questions. Then a synthesis pass into cited `research.html`. Postings lie about
location, title and openness — every JD claim gets checked against the company's own site.

**Build a résumé → workflow.** Fan the draft out per section — headline, summary, the three
skills blocks, the five experience roles — each agent working from `professional-journey.md`.
Then Rule 7 re-vectoring per job, fanned out the same way.

**EVERY workspace artefact is built by a subagent or workflow — no exceptions.** Set by him
2026-08-25. That means the whole build, not just the parts that look hard: `jd.md` and `jd.html`,
the weighted-rubric `index.html`, `resume_changes_for_<N>pct_match.html`, `bullets_for_upgrad.html`,
the re-vectored `upgrad_resume.html`, and cited `research.html`. Scaffolding with `resume.py new`
is a command, not authoring — but the moment content is being written into a workspace, it is
delegated.

**What stays in the main thread:** adjudicating what comes back, the adversarial verify pass, and
status changes through `./todo`. Coordination and judgement, never production.

**Score a JD → subagents, one per rubric criterion.** The **technical score is the one that
matters, and the target is 95+.** Give each criterion its own agent: weight, score out of ten,
and the evidence quoted from `professional-journey.md`. A separate agent names the **binding
constraint and the smallest honest lift** — which is almost always Rule 7 re-vectoring of real
work, never a new claim.

**Never fabricate to reach 95.** If honest evidence caps the score below 95, say so and name
exactly what is missing and what would close it. A 95 built on an invented claim is worse than
an honest 88, because the invented one gets found in the room. Read "e.g. / or / preferably"
generously — a specific named tool he has not used is a ramp item, not a capability cap — and
keep the non-technical score out of it entirely: informational, never a gate, never a drag on
the technical number.

**The verification phase is not optional, and it is what makes delegation safe.** Subagent
output runs roughly one factual error per ten claims, and this is a document where an invented
number is the cardinal sin. Every résumé workflow ends with adversarial agents checking each
claim back against the journey doc and the honesty rules above — anything unsupported is
**cut, not softened** — and you adjudicate the survivors yourself before a word reaches a file
he will paste. A claim that survives because no one checked it is a defect, not a result.

**Never delegate the open claims.** The confirm-or-reject list is his call alone. No agent
resolves the graph neural network, the four Rocket metrics, the 70–80% consolidation, the
27 ms / P95 16 ms pairing or the 100,000-concurrent wording. Surface them in every prep
artefact and leave the résumé wording alone.

**⚠ ARCHITECTURE — THE DATABASE IS THE SOURCE, HTML IS A VIEW.**

**✅ NO LONGER DEFERRED. He started it on 2026-08-27**, in his own words: *"remember, you SHOULD be
using a DB to store the information"* · *"AND prepare the HTML from that DB"* · *"starting now, we
do that"* · *"from the master resume"* · **_"DB is the source. No more grepping, etc etc"_**.

**What this means in practice, and it is a hard change of habit:**

- **The database is where résumé content LIVES.** Bullets, skills, the headline, the summary, role
  metadata, education, certifications and personal information. Not the file.
- **`master/upgrad_resume.html` is a GENERATED ARTEFACT.** Regenerate it; never hand-edit it. An
  edit made in the file is lost on the next generate, exactly the way an `UPDATE` against a derived
  table used to be lost on the next sync — the direction has simply reversed.
- **⛔ STOP GREPPING THE RÉSUMÉ FILES. Query the database.** *"No more grepping, etc etc"* is his
  instruction and it is the point of the whole change. Which bullets carry a number, which leading
  verbs are taken, what a role claimed for a given seat, where a metric appears — these are `SELECT`s
  now, not `grep -o` piped to `wc -l`. Every measurement trap this file records under
  *Measurement traps* came from parsing minified HTML with regexes. A query cannot mis-count a line,
  cannot match `p-e**lpa**so` for "LPA", and cannot mistake a Mermaid node id for Amazon S3.
- **Scope, stated precisely so the boundary is never guessed: the MASTER résumé only.** The eight
  per-seat workspace résumés are NOT migrated. Until they are, they remain files, and a sent one is
  never edited at all.

**⛔ THE GATE IS THE ROUND TRIP, AND IT IS NOT OPTIONAL.** Load the master into the database,
regenerate the HTML, and diff. **Byte-identical, or every difference enumerated and justified.** A
parse that silently drops a `<strong>` corrupts the master and would not surface until an exported
PDF lost its bold. **A lossy migration is the worst outcome available; stop rather than proceed.**
Until that proof passes for a given source, the FILE remains authoritative for it.

Do not half-migrate. A master résumé caught mid-migration across a session boundary is the worst
state to inherit.

The shape he set out, in his own words:

> 1. master resume has it's own bullets in a table · 2. you retrieve them, compare them to the JD ·
> 3. score & improve · 4. new bullets are stored in the DB again · 5. using these DB bullets, you
> export the PDF from upgrad · 6. **I only see the final PDF. if any changes are needed, you can
> make those changes to the DB** · 7. a HTML page that helps us with comparison, all running from
> the DB · 8. **HTML is no longer static. it's dynamic.**

**What he supplies is the MATERIAL, not the markup** — *"i give you the details of master resume,
which I've already done."* The journey document, the 17 VoltusWave bullets, the confirmations
(Kubernetes, Terraform, HIPAA, load balancing, high availability), and the corrections. He
adjudicates; he does not hand-author HTML. **His review surface is the exported PDF.**

**The collision, and how it resolves.** `upgrad_apply.py` parses `<workspace>/upgrad_resume.html`
by section id and pastes via `_paste_html`, which is still the only path carrying both bold and
bullets into the card. So the file is **generated from the database immediately before export** and
becomes a build artefact — regenerated on demand, never authored, never edited by hand. **The
exporter does not change.**

**Why this was needed.** Six full copies of his career existed across workspaces, all diverged, and
every one went stale silently when the master changed — the same duplication CLAUDE.md records
removing at the master level, recreated one level down. A per-seat résumé is a **selection with
edits**, not a copy.

**⛔ The migration's safety gate: it must ROUND-TRIP.** Parse the master into the table, regenerate
the HTML, and diff. Byte-identical, or every difference enumerated and justified. A parse that
silently drops a `<strong>` corrupts the master and would not surface until an exported PDF lost its
bold. **A lossy migration is the worst outcome available; stop rather than proceed.**

**What this makes enforceable rather than advisory:** leading-verb uniqueness across all ten roles,
≤25 words, at least one bolded fact, no trailing period. The verb list *"has been wrong before —
never trust it, regenerate from the file"* becomes a constraint instead of a warning.

~~**He still writes the master by hand.**~~ *(Superseded. He supplies the material and approves the
PDF; the markup is generated.)* The rest stands: Workflows draft, verify and stage paste-ready content;
they do not ship on his behalf, and they never touch the Hiration card.

**`./todo` coordinates, it never executes.** It answers what is due, what is blocked and what
is next, and records status changes with reasons. Do not grow it into a task runner. A workflow
may finish a task and report it; marking it `done` / `parked` / `pushed` / `dropped` goes
through `./todo`, and moving a task out always needs at least one reason.

## Measurement traps — every one of these cost real time on 2026-08-26

**The tool was wrong, not the data.** Each of these produced a confident, false finding that was
acted on before being caught. Check the measurement before trusting a measurement.

- **A word counter must ignore punctuation tokens.** A naive `split()` counts ` — ` as a word, so
  25-word bullets report as 26. Four bullets were trimmed that did not need trimming. Across every
  résumé in the repo there are **zero** genuine over-25-word bullets. Count only tokens containing
  `[A-Za-z0-9]`.
- **`grep -c` counts LINES, not occurrences — and these files are minified.** It reported 4 inline
  `span.note` uses when there were **63**. A per-page fix would have missed 59 of them. Use
  `grep -o … | wc -l`, or parse.
- **The LinkedIn slug lives in a PDF LINK ANNOTATION, not extractable text.** A text-only grep reads
  `abhisheikdeo` as missing on a perfectly good PDF. Read `/Annots` → `/A` → `/URI`.
- **Silent failure survives.** `src="../static/copy.js"` resolved nowhere from a workspace three
  levels down, so **every copy button on every tailored résumé was dead** — through six workspaces,
  because a missing script throws nothing. When a feature "should" work, prove it does.
- **A regex context window can be a false positive.** `p-e**lpa**so` matched an "LPA" compensation
  sweep; "hot-**spot**" matched a Fargate-Spot sweep; 36 "Amazon S3" hits were Mermaid node ids
  (`S2 --> S3`); "w**eeks**" matched EKS. Case-sensitive, word-boundaried, tag-stripped, or it is
  not a finding.
- **Dumping one source and generalising.** Dumping only `august_ic_master_resume` produced a
  confident, wrong conclusion that the 17 VoltusWave bullets did not exist. They were on the other
  card. **Enumerate the sources before concluding about "the" source.**

**On the adversarial verify pass:** it is what makes delegation safe, and it is not infallible. On
2026-08-26 it correctly cut a fabricated founder name, a figure welded from two incompatible
sources, and a wholly invented claim about a `score.json` — and it **missed two files** still
carrying "six continuous Spring Boot years". **Adjudicate the verifier too.** A claim that survives
because nobody checked the checker is still a defect.

## Working rules

- **Ask, don't assume.** At a fork, an ambiguity, or a missing input, invoke
  **`AskUserQuestion`** with 2–4 mutually-exclusive options — not a silent decision, and not a
  question buried in loose prose (asking in prose is the failure that created this rule). This
  overrides any bias toward working without stopping. Fine without asking: small mechanical
  follow-ups inside an already-approved task. Not fine: create-or-don't, the framing of an
  ambiguous identifier, or skipping a section. **One standing exception — a pasted JD always
  gets the full build. That fork is closed; do not re-ask it.**
- **Never run browser automation or screenshots to check rendering.** Verify pages return
  HTTP 200 against the running server and hand off; he does all visual checks himself.
- **Audit agent-written content.** Subagent output runs roughly one factual error per ten
  claims. Extract the claims, check each against the journey doc, then adjudicate.
- **Don't inflate a minor caution into a character judgement.** Rank findings by evidence,
  not by how bad they sound. Before advising that a "risky" detail be cut, ask what it is
  doing — it is often the load-bearing proof for the claim around it.
- **Code-derived findings have limits.** He no longer has access to some repositories, so
  any grounding pass reads a partial sample. **Absence in a partial sample is not absence
  in production.** Scope every finding to its repo, and ask him before reporting that code
  contradicts a résumé claim — this already produced one false alarm.
- **Verify JD claims against the company's own site.** Postings lie about location, title,
  and whether the seat is even open. A foreign city in a remote JD is usually a timezone
  anchor, not relocation — compute the overlap.
- **Relocation is open** and is not a scoring constraint. **6- and 7-day weeks are fine** —
  never ding a score for schedule density. Travel cadence and 24/7 on-call are separate
  axes worth surfacing.

**Interview prep lives in a different repo:** `~/Documents/interview-prep/`. This
workspace curates **jobs**; that one prepares for **rooms**. Prep material goes there,
résumé-creation material stays here, dual-purpose material gets copied to both.

**The v1 lesson on rooms.** Be precise about what actually happened, because the record
forbids guessing: one process ended in an **unexplained rejection with no recording** (EVA — no
reason given, expressly un-attributable), and the other he **withdrew from on his own read**,
with nothing formal ever arriving (CBRE — deliberately logged `closed`, not `not-selected`).
Neither cause is known. Do not write down that answer length, or a Kafka gap, or a .NET gap
lost either one.

The durable, evidenced lesson comes from a round he **passed** — CBRE round 1: **headline
sentence first, detail only if asked** (seven interruptions and three time warnings). He has
thousands of prep questions; more content is not the lever. Timed, out-loud, **recorded**
practice is. **Record every round** — one process produced no debrief at all because the
recording failed.

---

## Session handoff — `RESUME_SESSION.md`

**Read `RESUME_SESSION.md` first at the start of every session.** It carries what was in flight when
the last context was cleared and the single next action.

**Rewrite it whenever the context is about to be cleared, and whenever the picture changes
materially.** It is a living file, not a log — it describes the CURRENT state and the NEXT action.
Overwrite it wholesale; git carries the history. Keep it readable in a minute.

`PENDING.md` sits alongside it for run IDs and analysis that outlives one session. This Status
section stays the durable record; `RESUME_SESSION.md` is the "where were we".

## Company intelligence — gates, not scores

**These are real-world gates, named separately from both scores** and never allowed to drag the
technical number. Each belongs in that seat's `research.html`; this is the durable summary.

- **⚠ Yes Madam staged a fake mass-firing as a marketing stunt (December 2024).** A leaked HR
  email posted to LinkedIn claimed ~100 employees were fired over a workplace-stress survey; it
  went global within hours (Fortune, Business Standard, Gulf News). The company then said nobody
  was fired and it was "an awareness initiative", and announced six annual de-stress leaves.
  Mental-health advocates called it exploitation of a sensitive issue.
  **This is his highest-scoring seat (88.375). The flag is reputational, two years old, and worth
  asking about on a call — it is not disqualifying and must not touch the technical score.**
- **Yes Madam's business is genuinely working:** ₹50 Cr from Info Edge's B8 Fund in May 2026 (first
  institutional round), revenue ₹94 Cr → **₹195 Cr** FY26, monthly bookings ~70,000 → **~300,000**,
  55+ cities. Founded 2016, Gurugram. The new capital is earmarked for technology.
- **o9 Solutions is suing SAP for trade-secret misappropriation** (filed Nov 2025, N.D. Texas):
  former o9 executives allegedly downloaded tens of thousands of files before joining SAP. By
  January 2026 SAP had separated from all three. Valuation $2.7B (2022), marked to $3.7B (2023),
  IPO on the horizon.
- **⚠ o9's architect track specifically is where its reviews turn.** Bengaluru: 3.2/5 work-life
  balance, 76% would recommend against 86% company-wide; complaints of 7am-to-midnight call
  windows, slow career growth, regional politics. **Associate Solutions Architect: 42% would
  recommend, down 18 points in twelve months** — the closest role family to the seat.
- **Wipro is managing cost, not growing headcount:** layoffs May 2026, attrition 13.8%, fresher
  hiring guidance cut roughly in half, contract cancellations as US clients in-source or replace
  work with AI tooling. Corroborates the workspace research independently.

**⚠ `/last30days` returned NOTHING on any of these companies.** Verified 2026-08-26: every Reddit
cluster came back tagged *entity-miss demotion* — generic r/developersIndia and r/india noise, zero
items actually about the companies. Only **1 of 8 sources was active** (no X auth, no `yt-dlp`, no
ScrapeCreators key). **There is no live social signal on these employers; anything claiming recent
buzz is invented.** All findings above come from web supplements and are older than 30 days. If the
social layer matters later, X auth and `yt-dlp` are the two cheapest unlocks.

---

## Status — 2026-08-26, ~18:15

**FOUR APPLICATIONS SENT TODAY. That column was empty this morning.** v1 died with 23 built and
unsent; the pattern is broken.

| seat | status | tech | contact |
|---|---|---|---|
| keyloop-principal-architect | **ready** | **89.6** | — |
| modmed-senior-software-architect | applied | 88.9 | Prabhakar Teguri, in-house |
| yes-madam-lead-architect | applied | 88.375 | — |
| conde-nast-principal-engineer | **ready** | 87.4 | **Lokesh Reddy Guntaka, in-house** |
| principal-architect-ai-native | applied | 84.9 | — |
| o9-senior-architect-agentic | applied | 81.4 | — |
| wolters-kluwer-…-ai-platform-engineer | **withdrawn** | 69.9 | Paul Abbott, Andela |
| wipro-principal-software-architect | awaiting JD | — | Harisri Parthasarathi |

**Every seat has a verified PDF except Wipro**, which has no job description and so no score.

**Wolters Kluwer was withdrawn on his call** — *"hands-on Python 5+ years in production which will
not work out for me."* The 5+ figure is the **Lead** bar, the fallback offered, so neither role
cleared it. Production Python is ~14 months: a duration fact, not a wording problem.

**⚠ Condé Nast is the third encounter with one seat.** v1 built it 21 Jul (96, never applied) and
again 6 Aug after an inbound InMail from an in-house recruiter (96, **reply never sent**). Twenty
days passed; the seat was reposted. All v1 work is preserved under
`August-2026/26/conde-nast-principal-engineer/v1/`. **Scored fresh at 87.4 rather than inheriting
96** — the gap is the agentic-scope open claim, which v1 credited more generously.

**Built this session:** the v1/v2 database split with all SQL in `db/` · `application_events` as the
correspondence timeline with verbatim messages · the launcher rendering from `jobs_tracker_v2` in
v1's tab shape · the daily log as a Kanban board that refuses a reason-less move · PostgreSQL
migrated 16 → 18 · `serve.py` binding both loopback families · `resume.py new` refusing without a
posting URL · six full workspaces with research, rubrics, tailored résumés, verified PDFs and staged
outreach.

**Decided this session:**

- **The database is authoritative for what HAPPENED; the files for what is CLAIMED.** Query status,
  dates, scores, contacts and the timeline; read the files for bullet text, hygiene and the honesty
  checks. `db/README.md` carries the cheatsheet.
- **The database becomes the source, HTML a view, the PDF his review surface** — approved for
  **later**, design in `db/DESIGN-bullets.md`, schema prepared, **round-trip proof passed**
  (458 bullets byte-identical, 0 tag differences, `<strong>` preserved).
- **Always capture the posting URL at intake.** The tool refuses without one.
- **Compensation is deferred entirely** until a company reaches that stage.
- **A sent résumé is history.** Migration 011's trigger makes editing one impossible, not merely
  discouraged.

**Still his hand:** landing `master/merge_proposal.html` into the master (which still has zero hits
for Kubernetes, Terraform, Jenkins, GitHub Actions) · El Paso's three card bullets still reading
.NET · the ModMed résumé lacking the words "domain-driven" though the JD names it.
