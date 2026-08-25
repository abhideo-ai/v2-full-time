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
- **Fresh verbs — older roles only — still free: Translated, Calibrated. That is all.**
  Thirteen of the original fifteen went into the master.
- **Verified free against the master, for Rule 7 top-ups:** Instrumented, Replatformed,
  Brokered, Piloted, Eliminated, Halved, Bridged, Curated, Seeded, Salvaged, Trimmed.
  *(Extracted, Hardened, Sequenced and Secured moved to the used list on 2026-08-25.
  `Built` is NOT free — `Build`-versus-buy sits mid-bullet in the skills block.)*

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

**Compensation:** current **₹72L**, expected **₹75L–₹1Cr**. The ₹75L floor is a ~4% step,
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
  park, push and drop with its reasons and timestamp. Schema: `automation/schema.sql`;
  migrations in `automation/migrations/`.
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
  and the launcher card registered as `building`. Everything repeated 15–20 times a night.
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

**Default to the Workflow tool for anything substantive**, and fan the work out to
**subagents**. Read each phase's results before choosing the next phase. Solo only for
conversational turns and trivial mechanical edits.

**Research a job → workflow.** A multi-modal sweep, one agent per angle: the company's own
site, comp signals, the seat's legitimacy and whether it is even open, red and green flags,
forcing questions. Then a synthesis pass into cited `research.html`. Postings lie about
location, title and openness — every JD claim gets checked against the company's own site.

**Build a résumé → workflow.** Fan the draft out per section — headline, summary, the three
skills blocks, the five experience roles — each agent working from `professional-journey.md`.
Then Rule 7 re-vectoring per job, fanned out the same way.

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

**He still writes the master by hand.** Workflows draft, verify and stage paste-ready content;
they do not ship on his behalf, and they never touch the Hiration card.

**`./todo` coordinates, it never executes.** It answers what is due, what is blocked and what
is next, and records status changes with reasons. Do not grow it into a task runner. A workflow
may finish a task and report it; marking it `done` / `parked` / `pushed` / `dropped` goes
through `./todo`, and moving a task out always needs at least one reason.

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

## Status — 2026-08-25, end of session

**The master résumé is written.** `master/upgrad_resume.html` — one file, ten parsed sections
plus the card-only material, verified against the real parser, **27 experience bullets with 27
unique leading verbs**. New headline and summary carrying the Amura work, four new Engineering
Excellence lines, four new VoltusWave bullets, and the Neptune→Elasticsearch correction.

**⚠ His live Hiration card is still the v1 LEADERSHIP résumé and must be rebuilt.** It says
*"Engineering Leader"* in the headline and *"Engineering Manager"* in the summary, carries
**no Java anywhere**, asserts *"Neptune + GNN"* and *"GNN models in production"*, claims ISO 27001,
and opens with the typo *"ands-on"*. None of that is in the master here. Rebuilding the card from
`master/paste_sheet.html` is the next physical step, and it is his hand-work.

**Built this session:**

- **The daily log** — `daily/index.html` from `daily/days.json`, state in PostgreSQL (`v2_daily`),
  `automation/serve.py` replacing `http.server`, `./todo` on the command line. Priorities,
  dependencies, rollover, move-out with reasons and revivability. 36 + 50 test assertions.
- **`automation/resume.py`** — `new` scaffolds a job workspace, `sheet` generates the paste sheet.
- **The case studies** — `killer-query-case-studies/` (v1, all shipped), a `summary.html` with the
  concept glossary, and ten per-query interview-prep pages under `prep/`.
- **One master file** — `master_paste.html` and `upgrad_resume.template.html` folded in; the parser
  now reads `<p>` bullets as well as `<ul><li>`, which is what made that possible.

**The plan he set for tonight (25 Aug, from ~19:20, running into the morning):**
build the Hiration card, export and verify the master PDF, then **15–20 job workspaces**. He pastes
the JDs; we build. The bot exports serially on one shared browser, and he has accepted that queue.

**Decided this session — all recorded in the sections above:**

- Workflows and subagents do the work, including résumé creation and JD scoring, with a mandatory
  adversarial verify pass. Technical score is the one that matters, target 95+, never fabricate.
- He pastes JDs; **we do not source seats**, and we do not re-rank or recommend an order unasked.
- A copy block is **one whole section that replaces its counterpart**, never a fragment.
- **Redis is claimable.** Everything in the v1 case studies **shipped**. There are **no Amura
  outcome metrics** — scale and design markers only. The **25–30% infrastructure cost** and
  **hours → under 10 minutes** deploy time are **user-confirmed**; do not re-flag them.
- v2 of the case studies lands beside v1, never over it — but **do not wait for it**.

**Open — his call alone, nothing here is ours to settle:**

- **The +65% hotel conversions**, live on the résumé. The journey doc flags it twice as unresolved
  and his original has no 65% conversion claim at all. The evidenced alternative sits unused:
  *"screens lading time was improved by 60-70%"* at innRoad, in his own handwriting.
- **VoltusWave carries 10 bullets** — six chat-platform, four Amura — and will not fit three pages.
  Trimming is per-job, not a master edit.
- ~~ISO 27001~~ — **SETTLED 2026-08-25: Deque's certification, and the environment he delivered
  in.** Written as "HIPAA pipelines in an ISO 27001-certified environment", never as a credential
  he personally holds.
- **Confirm-or-reject:** ~300 customers vs instances; the 70–80% consolidation; two Rocket metrics
  (bugs −50%, sales +20%); 8% month-over-month sustained or one-time; the 100,000-concurrent
  wording, currently written as burst testing.
- **The large language model narrative guardrails.** Split, not yes-or-no: KQ1's claim grammar is
  live inside its retrieval service, but KQ9's shared contract is unsigned and its narrator ships
  **off by default**. A bullet claiming KQ9 must carry KQ9's hedge.
- **El Paso on the card** — the v1 card calls it .NET; it is a Senior Java Developer role, and
  leaving it hides four of the eleven Java years.
- **The journey document now lags the master** on the entire Amura programme, and it is meant to
  lead. Folding that material back in is `journey-doc`, P1 on `./todo`, and he has said it is the
  task that matters most to him.
