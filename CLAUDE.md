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

`master/upgrad_resume.html` **does not exist yet and must be authored** from the journey
doc against `master/upgrad_resume.template.html`. Nothing exports until it does. See
`master/README.md` for the ten-section parser contract and its silent failure modes.

---

## Honesty — load-bearing

If it is not in the journey document and not user-confirmed, do not write it. A missing
metric is `[fill in metric]`, never an invented number.

**Never claim:** Kafka (he has **Amazon Kinesis**, confirmed in production), MongoDB,
ClickHouse, Azure, Google Cloud Platform, Redis, SOC 2, Spring Cloud, Spring WebFlux,
Spring Batch. Only **Spring Boot** is his.

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
- **The VoltusWave org was 6 sub-teams** — backend, React Native, web, artificial
  intelligence, quality assurance (QA), DevOps. Never "5". He hired QA engineers.
- **Safe to claim:** Django, FastAPI, LangChain, LangGraph, real Model Context Protocol
  (MCP) servers, Deque role-based access control and US–India teams, least-privilege,
  React (web), a measured Claude Code / Codex rollout, Datadog. Metrics: hotel conversions
  **+65%**, ELK cost **−46%**, 8 early clients, and **25 hotel suppliers integrated through a
  MuleSoft enterprise service bus** — all four user-supplied and safe to claim.

**Open claims — HE settles these, not us.** Never rewrite them in either direction on your own
initiative; surface them in every technical-round prep artefact and leave the résumé wording
alone until he decides. The journey doc *asks* several of these questions, so it cannot resolve
them for you.

- The **graph neural network** — shipped, or still in training? Never upgrade it to
  shipped-and-serving.
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

- **Used — do not reuse as leading verbs** (all 23 leading verbs in the master):
  Architected, Scaled, Deployed, Delivered, Engineered, Drove, Implemented, Steered, Forged,
  Productized, Stewarded, Championed, Anchored, Coached, Surfaced, Partnered, Co-founded,
  Mobilized, Helmed, Codified, Cut, Reconciled, Lifted.
- **ATS power verbs — current role ONLY — still free:** Secured, Optimized, Strengthened,
  Built, Spearheaded, Improved, Increased. *(Established, Launched, Designed, Reduced and
  Owned are burnt — their roots appear mid-bullet as establishing / launched / design /
  reducing / ownership.)*
- **Fresh verbs — older roles only — still free: Translated, Calibrated. That is all.**
  Thirteen of the original fifteen went into the master.
- **Verified free against the master, for Rule 7 top-ups:** Extracted, Instrumented, Hardened,
  Replatformed, Brokered, Piloted, Eliminated, Halved, Bridged, Curated, Sequenced, Seeded,
  Salvaged, Trimmed.

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

**(1) TECHNICAL — target 95+.** Engineering capability. Read "e.g. / or / preferably"
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

- **`august_ic_master_resume`** — the IC card, hand-built 2026-08-25 from
  `master/master_paste.html`. **This is the default choice for the IC-only track.** It is
  *not* the script default, so every export needs `--master august_ic_master_resume` or
  `UPGRAD_MASTER_CARD=august_ic_master_resume` in the environment.
- **`august_master_resume`** — kept deliberately. It may still be used for future positions.
  It is what `upgrad_apply.py` falls back to when no `--master` is passed, so **an export with
  no flag silently uses this one** — pass the flag or check which card you got.

### ⛔ Card deletion — ask first, every time

**Never run `cleanup_cards.py` at all until he explicitly says to delete a specific card.**
Not after an export, not after a submission, not as tidy-up. He asks, by name, or it does not
run. A bare, slug-less run deletes every temp card; even `--slug <slug>` is his call to make,
not a follow-up to infer. Tailored `<slug>_ats_resume` cards accumulating is the intended
state, not a mess to clean.

**⚠ Dates live in the Hiration card, not the HTML.** The bot overwrites bullet text only, so
the card itself must already read Apr 2026. **Education, certifications and the pre-2016 roles
are card-only too** — the bot never touches them; edit those by hand in the Hiration UI.

**Verify every exported PDF:** dates correct (VoltusWave ended **Apr 2026**), bold renders
heavier, content matches `bullets_for_upgrad.html`, contact details and the LinkedIn slug
**`abhisheikdeo`** (not `abhideo` — that is the email domain), no `[fill in metric]`, and
**≤3 pages**. The ATS "Resume Review" score wobbles 87–99 on hygiene, not JD
fit — don't chase it. (No print dialog is involved: the bot exports headlessly and
`html_to_pdf.py` uses Playwright's own PDF call. If a résumé PDF ever comes from a source
document instead, export it from that application rather than via the browser's Print to PDF,
which flattens bold.)

`automation/html_to_pdf.py` renders any workspace HTML to PDF via headless Chromium.

### upGrad paste quirk

upGrad keeps raw `<strong>` but **strips styled `<span>`s, and strips bold from
list-rooted content**. So `bullets_for_upgrad.html` restates each changed bullet as a
standalone `<p>` with raw `<strong>` — never inside a `<ul>`.

### Naukri quirk

Naukri's "Job profile" textarea rejects `<` and `\`. Substitute: `<` → `under` / `below`,
`≤` → `within` / `at most`, `≥` → `at X+` / `above`.

---

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

## Not built yet

Deliberately absent, to be created as the pipeline restarts:

- `master/upgrad_resume.html` — author it from `professional-journey.md`.
- The root `index.html` dashboard and per-workspace launcher pages.
- Any job workspaces.
