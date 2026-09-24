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
`resume_changes_for_<N>pct_match.html` · cited `research.html` (verdict, red/green flags,
forcing questions — **never compensation**) · `score.json` · then the generated **and verified**
per-seat `.docx`.

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

## Resume Writing Points

- base resume is the master resume at `/Users/adeo/Documents/v2-full-time/master/Abhisheik_Deo_Resume.docx`
- for every job description, give me a new version of the master resume in the company's slug that'll match the JD at 95+%.
- the points will need to be added in the last 5 companies namely: (i) Voltuswave (Principal Software Architect), (ii) Deque Software, (iii) Rocket 
  Software, (iv) Voltuswave (Co-Founder & VP of Technology) & (v) Teletext India.
- You'll have to give me a HTML page as well that'll allow me to verify and if needed to copy/paste for each of the 5 organizations.

For every job description, change the "master resume" present in `/Users/adeo/Documents/v2-full-time/master/Abhisheik_Deo_Resume.docx` 
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

### Verb pool — regenerate it, never read it from a list

**⛔ DO NOT KEEP A VERB LIST IN THIS FILE.** One lived here and was wrong twice: nine verbs
documented as free were already leading bullets, and `Hardened` and `Extracted` were duplicated
across roles because only the five parsed roles had been checked. The résumé now lives in
PostgreSQL, so the list is a query and cannot be stale:

```sql
-- every leading verb currently in use, across ALL TEN roles
psql -d jobs_tracker_v2 -At -c "select b.leading_verb from resume_blocks b
  join resume_sections s on s.doc_key=b.doc_key and s.section_id=b.section_id
 where b.doc_key='master' and s.section_kind='experience'
   and b.retired_at is null and b.leading_verb is not null order by 1;"

-- is a candidate free? SAME-ROOT COLLISIONS COUNT AND THEY HIDE MID-BULLET,
-- so check the stem across the WHOLE document, not just leading words.
psql -d jobs_tracker_v2 -At -c "select section_id, ord, substring(text,1,70)
  from resume_blocks where doc_key='master' and retired_at is null and text ~* '<stem>';"
```

**Never `Managed` / `Replaced` / `Responsible for` / `Worked on` / `Helped`.** `Orchestrated`
leads a Deque bullet, so the stem `orchestrat` is burnt. `Built` is not free — *Build*-versus-buy
sits mid-bullet in the skills block.

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

- Workspaces: `Month-YYYY/DD/<slug>/` → repo root `../../../`. Raw inputs:
  `job-applications/Month-YYYY/DD/`.
- **No per-file `<style>` blocks.** Shared classes live in `style.css`.
- **All SQL in this repo lives in `db/`** (`db/migrations/`, `db/schema.sql`, `db/README.md`), so
  every schema and data change is re-runnable and verifiable later.

**⚠ TWO upGrad-NAMED SCRIPTS ARE NOT RETIRED** — hoisted here 2026-09-21 when the rest moved to
`docs/RETIRED-upgrad-pipeline.md`; both govern CURRENT behaviour and would have gone with it.

- **⛔ `automation/upgrad_resume_paste.py` IS THE SHARED RÉSUMÉ PARSER**, despite the name —
  imported by `resume_db.py`, `jobs_sync.py`, `daily.py`, `resume.py`, `workspace_favicon.py`.
  **Load-bearing for the current path, deliberately NOT guarded** by `upgrad_retired.py`. Never
  "clean it up" with the others.
- **⛔ `automation/cleanup_cards.py` IS STILL NEVER RUN** — not after an export, not after a
  submission, not as tidy-up. He names a specific card or it does not run; a bare slug-less run
  deletes every temp card. Accumulating `<slug>_ats_resume` cards is intended, not mess.

### The launcher renders from the database

`index.html`'s Applications list renders from `jobs_tracker_v2` via `GET /api/jobs`. **Never
hand-write a row into `#app-list`** — no query can see it; that is how the page showed
4 applications over 92 database rows.

- **One row per slug, grouped by intake date**, v1's shape: underlined text tabs with count badges,
  right-aligned search box, `COMPANY · TITLE · TECH · NON-TECH` strip per group, expandable detail row.
- **v1 AND v2 ARE SEPARATE DATABASES** — *"let's use a different database? like `jobs_tracker_v2`?
  this way we DO NOT interfere with v1 jobs?"* `jobs_tracker` is v1's record, **92 seats, frozen,
  nothing in v2 opens it**; `jobs_tracker_v2` holds v2's seats only. `db/migrations/` 004 creates
  it, 005 moves the seats, 006 reverses the archive. Verify all three databases read-only:
  `psql -d postgres -f db/verify.sql`.
- `automation/jobs_db.py` — read-only queries (`JOBS_TRACKER_DSN`, default `dbname=jobs_tracker_v2`).
  `automation/jobs_sync.py` — registers a seat, refreshes technical scores from each workspace's
  `score.json`; idempotent, re-run after any re-scoring.
- **Six tabs over eleven statuses, deliberately no `all`** — `Ready to apply · Applied · No longer
  available · Heard back · Not selected · Other`, v1's set exactly; mapping and two-score derivation
  in `automation/README.md`. `recommended_skip` → **Other**, so those rows never drag on the
  ready-and-unsent backlog gate.
- **⛔ NO `archived` TAB, NO ARCHIVE CONCEPT.** `db/migrations/003` archived v1's 92 rows in place
  for a day; `006` reversed it. A row that must be filtered out of every view belongs in the other
  database. Not in `TAB_FOR_STATUS`, `TABS`, or `jobs_tracker_v2`'s enum. **Never re-run 003.**
  (No `DROP VALUE` in PostgreSQL, so `archived` survives inert in `jobs_tracker`'s enum.)
- **A v1-rubric row's scores read `v1`, not a number** — five-axis triage rubric, and `technical 20`
  beside `technical 88.4` implies a ranking that does not exist. `jobs_sync.py` refuses to overwrite
  a five-axis breakdown, so the two rubrics can never silently merge.
- **Group headers: `<date> — N seats`, nothing more** — date and count are derived; a sentence
  characterising a group of seats is not, and is never composed. Extra clauses are hand-authored in
  `automation/intake_notes.json`, which ships empty.
- **⛔ `applications.salary` is never selected or rendered** — compensation is deferred.
- Under plain `http.server` there is no API: the page **says the list is unavailable**, never an
  empty grid.
- **Counts derive from the DOM rows** — `static/tabs.js` re-derives on a `MutationObserver` over
  `#app-list`; `DOMContentLoaded` alone read 0 on every tab above a full list, because rows arrive
  from `/api/jobs` long afterwards.

### Capture the history — `application_events`

*"we should capture our history properly."* `status_events` records only `resume_drafted → applied`
— not an InMail arriving, a reply going out, two JDs back four hours later, a CV requested. **v1 had
none of it**; two processes closed with nothing recorded.
`db/migrations/009_application_events.sql` creates the timeline. Six kinds: `inbound` · `outbound` ·
`document` · `call` · `status` · `note`.

- **`actor` is REQUIRED** — *"Someone sent a JD"* is a record you cannot use later. A named human
  for their side, `Abhisheik` for his.
- **`detail` is the message VERBATIM** where one exists; a paraphrase six weeks later is not
  evidence of what was said. Paul Abbott's two messages and Harisri Parthasarathi's InMail are
  stored in full.
- **`artefact`** is the repo-relative path when a file changed hands (a JD PDF, an exported résumé).
- **Append-only: correct by adding an event, never by editing one.**
- **Log one every time anything happens** — InMail in, reply out, document exchanged, call
  scheduled or held. One command, against the v1 lesson.

```
psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select
     set_config('ev.slug','<slug>',false), set_config('ev.kind','inbound',false),
     set_config('ev.actor','<who>',false), set_config('ev.summary','<one line>',false),
     set_config('ev.detail','<verbatim>',false), set_config('ev.at','<ISO ts>',false)" \
  -f db/operations/log_event.sql
```

### The daily log

`daily/index.html` — due, blocked, next. **Generated, never authored:** `daily/days.json` is the
source, `automation/daily.py` owns the markup.

```
automation/.venv/bin/python automation/serve.py   # NOT `python3 -m http.server 8006`
automation/.venv/bin/python automation/daily.py   # regenerate the page from days.json
./todo   # what's due, from the terminal   ./todo backlog   # what moved out, what can come back
```

- **State lives in PostgreSQL (`v2_daily`)**, not the HTML, not the browser: `task_state` is what
  the page renders, `task_event` is append-only history — every tick, park, push and drop with its
  reasons and timestamp.
- **`serve.py`, not `http.server`** — same port 8006 so a pinned tab keeps working; adds the state
  API, sends `no-store` so a refresh really refreshes, binds `127.0.0.1` because it writes to a
  database. Under plain `http.server` the page falls back to localStorage and says so in the banner.
- **Each task carries a priority and dependencies**; unticked prerequisites mark it *waiting*, never
  disabled — out of order is legitimate.
- **Unfinished tasks roll over automatically** — never duplicate one in `days.json` to carry it forward.
- **Moving a task out always needs at least one reason**, and the reasons decide revival: revivable
  only if **every** reason it carries is `revivable` in `days.json`; one terminal reason — the
  posting is gone — closes it. With no reason and no terminal to ask on, the CLI refuses rather than
  inventing one. Deliberate: an agent has to come back and ask.
- Tests: `bash automation/tests/run.sh` (the page suite needs `npm install jsdom`).

### Making a résumé, and its paste sheet

```
automation/.venv/bin/python automation/resume.py new   --slug <slug> --url <posting URL> [--company X --role Y]
automation/.venv/bin/python automation/resume.py sheet [--slug <slug>] [--since <git-ref>]
```

- **`new`** scaffolds the workspace: dated directory, `upgrad_resume.html` copied from the master,
  empty `paste_notes.json`, a `jd.md` to paste into, a per-workspace favicon, and a `resume_drafted`
  row in `jobs_tracker_v2` the launcher shows under *building*. 15–20 times a night. **Refuses without a
  posting URL**: pass `--url <posting URL>`, or `--no-url "<reason>"` when the seat genuinely has
  none (see *Intake flow*).
- **`sheet`** emits `<workspace>/paste_sheet.html` — each section as ONE copy block, generated
  **from** the résumé so it cannot disagree with it. Changed sections come from a git diff;
  `--since <ref>` is needed once the change is committed, because diffing a committed file against
  HEAD correctly reports nothing changed. The *reason* a section changed cannot be derived — it
  comes from `paste_notes.json` (`{"quick-summary": {"why": …, "heads_up": …, "hygiene": …}}`), and
  a changed section with no note says so rather than inventing one.
- `automation/add_breadcrumbs.py`, `automation/expand_acronyms.py` — idempotent, safe to re-run when
  new pages land.

### Case studies — VoltusWave · Amura

`killer-query-case-studies/` is **v1**: ten killer-query case studies plus Q&A companions,
~198,000 words on Amura, a chronic-care platform covering 80+ conditions. Complete, committed
(46227bd), verified against the corpus 2026-08-25.

- **All of v1 SHIPPED — he confirmed it.** Never let an extraction downgrade it: the source says
  *"the contract was signed and the query is live"*, and *"approval pending"* is an internal
  **design-review sign-off**, not deployment status — a first pass misread the two and under-claimed.
- **⚠ He has NO outcome numbers** (he left VoltusWave before capturing them). Latency achieved,
  adoption, error reduction, cost saved: `[fill in metric]` or absent — never invent one, and never
  ask him again for a number he has already said he does not have. Amura bullets carry **design and
  scale markers only**: 80+ conditions, a 6-hour cache TTL, a 90-day outcome-maturity window,
  twenty adversarial-review findings absorbed into a hardened v2, 13 of 13 local findings closed,
  and — user-supplied, safe to claim — **9–10 years of patient history**. That last is load-bearing,
  not decorative: as-of featurisation, leakage-safe labelling, 90-day outcome maturity and sequence
  mining mean nothing without years of longitudinal data behind them.
- **⚠ THE WORST HONESTY LANDMINE IN THE CORPUS — KQ2's illustrative served-cell table.**
  `kq2-outcome-correlation.html` prints `Metformin + concurrent nutrition | 412 | 0.58 |
  [0.53, 0.63]` against `Metformin alone | 217 | 0.34 | [0.28, 0.41]`, `+24 percentage points` and
  `max SMD 0.08` over eight covariates — formatted exactly like a measured result. Its own label,
  which the prep page says to speak aloud: *"**Illustrative response shape, not a production
  measurement.**"* **None of 412, 217, 0.58, 0.34, +24pp or 0.08 may ever appear on a résumé or in a
  room as an outcome.** Same class: KQ1's *"300 patients in India on protocol A"* — an illustrative
  example, not a cohort size.
- **⚠ Amura names NO message broker** — `Kafka` 0 hits and `Kinesis` 0 hits corpus-wide; the source
  deliberately says only *"its streaming transport"*. **The master's Kinesis bullet is the CHAT
  PLATFORM, a different system** — keep them apart, never cite Amura as Kinesis evidence. (Kinesis
  stays confirmed in production for the chat platform.)
- **The 6-hour cache TTL is KQ4's, not KQ1's**: `kq1-precedent-search.html` is **TTL 1h**,
  `kq4-early-signal-detection.html` **TTL 6h** — both safe markers, each on the right query.
  **`TraversalSource` is corroborated in substance but not by that name**: KQ9 says *"tenant-scoped
  traversal-source wrapper"*, which is how to write it.
- **Do NOT wait for v2** — build bullets, workspaces and prep artefacts off v1 now; v2 is
  **days-to-weeks away** and holding work back for it is the build-instead-of-send failure in a
  different hat. It lands in `killer-query-case-studies-v2/`, **never overwriting v1**
  (`professional-journey-original.md` line 231 and the launcher link point at v1 and stay valid, and
  side by side is what makes the diff possible). Then extract v2, diff it against v1, revise only
  what moved — **honesty work, not bookkeeping**: a claim moving *shipped* → *designed* between his
  own two versions must never reach a résumé as shipped. Any downgrade binds.
- **Status vocabulary, from the source and never upgraded:** `shipped-production` ·
  `shipped-ci-only` · `designed-reviewed` · `designed-only` · `unclear` — the material draws the
  line itself (*"components landing does not by itself convert a review verdict"*), and anything
  derived from it inherits that precision.


> ## ⛔ THE upGrad / HIRATION PIPELINE IS RETIRED — moved out of this file 2026-09-21
>
> **His upGrad access was revoked on 2026-08-27.** Résumé layout and PDF export are done by hand
> in Canva Pro, and the current delivery path is `jobs_tracker_v2` → `.docx` (see *Layout &
> automation*). Every upGrad entry point refuses with exit 3 (`automation/upgrad_retired.py`).
> **Do not try to revive it, and do not diagnose the refusal as a bug.**
>
> The full history — upGrad export, which master card, card deletion, copy blocks, the Hiration
> paste matrix, editing the card, the paste quirk — is preserved verbatim in
> **`docs/RETIRED-upgrad-pipeline.md`**. All nine scripts and both Hiration cards stay on disk;
> he said so explicitly: *"do not remove the files. just remove the step from the automation
> workflow."*
>
> ⚠ **`master/live_card_dump*.json` and `.md` are the ONLY surviving record of what those two
> cards contained.** They cannot be refreshed. They are committed; keep them.
>
> ⚠ **`master/Abhisheik_Deo_Resume.SUPERSEDED-2026-08-25.pdf` is the last upGrad export and it is
> WRONG** — Knockout.js, 300, no AngularJS/280/Kubernetes. **It must never be sent.**

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

*Every rule here is his, on the date given; italic quotes are his words verbatim.*

### ⛔ AGENT BUDGET — MAX 5 (2026-09-20). This bounds everything below it.

**No workflow spawns more than 5 agents; no turn spawns more than 5 standalone Agent calls.** Five
is enough here, and this rule comes FIRST — "offload everything" operates inside it, never around
it. **If a task genuinely needs more, say so and ask**; never spend it and explain afterwards.

- **Bound every fan-out:** `items.slice(0, 5)`, never a bare `parallel(items.map(...))` over a
  data-dependent list. Over five, pick the five that matter and **`log()` what was dropped** —
  silent truncation reads as "covered everything".
- **⛔ NEVER nest `parallel()` inside a `pipeline()` stage — that MULTIPLIES.**
  `pipeline(edits, e => parallel(LENSES.map(...)))` over 22 edits × 3 lenses is **66 agents**; on
  **2026-09-20** it was 70 in one workflow, ~89 across the session, where ~17 was right —
  *"70 agents for this task? that's a bit much."*
- **Verification depth scales with RISK, not uniformly.** That same blowup gave a one-word
  skills-label tweak the full three-lens adversarial treatment. Triage: only edits asserting new
  substance need it.
- **Deterministic checks are SCRIPTS, never agents** — word count, bolded fact, trailing period,
  leading-verb stem collisions, acronym expansion are `psql` queries and `verify_resume_docx.py`,
  already written. A model counting words is wasteful *and less reliable*; see *Measurement traps*.
- **Ultracode's "token cost is not a constraint" is NOT a licence to skip proportionality.** Cheap
  and warranted are different questions; the budget holds regardless.

### ⛔ THE REAL GOAL: KEEP THIS CLI ANSWERABLE. Restated by him 2026-09-21.

*"The real goal: Keep this main CLI ready for accepting tasks/answering questions."* **That is WHY
work is delegated — not because agents write better.** A thread busy producing cannot take the next
pasted JD, a redirect or a question; at ~20 workspaces a night, availability beats any single
artefact. Hence (2026-08-25, default not preference): **if it CAN be offloaded to a subagent or
workflow, it IS** — research, résumé drafting, JD scoring, workspace artefacts, extraction, audits,
drafting of any kind. **The test is not "is this hard enough to delegate" — it is "does this have
to be me".** Almost nothing does; feeling it faster to write than to brief is the instinct that
blocks the thread for twenty minutes.

Three consequences, all violated on 2026-09-20:

- **"It's only mechanical" is not an exemption.** Transcribing a JD into `jd.md`, hand-writing
  `score.json`, composing bullet text — each felt faster, each blocked the thread. **Content
  landing in a workspace is delegated;** only existing commands and judgement are typed here.
- **Launch in the background, then TALK TO HIM.** Polling a running workflow is the blocked thread
  in disguise: launch, report it in one line, stay available — the completion notification arrives
  on its own.
- **Adjudication stays here** — quick, and the one thing only this thread can do.

**How this squares with the 5-agent budget: the cap is PER WORKFLOW**, so a full workspace is three
or four sequential background workflows of ≤5 agents each, never one big fan-out:

```
phase 1  scoring + research          -> <=5 agents, background
phase 2  re-vectoring + verification -> <=5 agents, background
phase 3  the page artefacts          -> <=5 agents, background
```

Between phases the thread is free for an interrupt, a redirect or the next seat — that is the
point. **Read each phase's results before choosing the next.**

**Main thread only — coordination and judgement, never production:** **adjudicating** what comes
back and the **adversarial verify pass** against `professional-journey.md`, which is the only
reason delegation is safe · **his decisions** — the confirm-or-reject list, what to send, what to
trim · **coordination** — the next phase, and status changes through `./todo` · conversational
turns, and running a command that already exists. Everything else goes wide.

**EVERY workspace artefact is built by a subagent or workflow — no exceptions** (2026-08-25):
`jd.md`, `jd.html`, the weighted-rubric `index.html`, `resume_changes_for_<N>pct_match.html`,
cited `research.html`, and the per-seat `.docx`. Scaffolding
with `resume.py new` is a command, not authoring — but the moment content lands in a workspace, it
is delegated.

- **Research a job → workflow.** One agent per angle — the company's own site, comp signals, the
  seat's legitimacy and whether it is even open, red and green flags, forcing questions — then
  synthesis into cited `research.html`. Postings lie about location, title and openness — every JD
  claim gets checked against the company's own site.
- **Build a résumé → workflow.** Fan the draft per section — headline, summary, the three skills
  blocks, the five experience roles — each agent from `professional-journey.md`; then Rule 7
  re-vectoring per job, fanned the same way.
- **Score a JD → subagents, one per rubric criterion.** **Technical score is the one that matters,
  target 95+**: each criterion gets its own agent (weight, score out of ten, evidence quoted from
  `professional-journey.md`), plus one naming the **binding constraint and the smallest honest
  lift** — almost always Rule 7 re-vectoring of real work, never a new claim.

**Never fabricate to reach 95.** Read "e.g. / or / preferably" generously, treat a named tool he
has not used as a ramp item and not a capability cap, and keep the non-technical score out
entirely — informational, never a gate, never a drag (detail in *JD match scoring*). If honest
evidence caps the score lower, say so and name what is missing and what would close it: a 95 on an
invented claim is worse than an honest 88, because the invented one gets found in the room.

**The verification phase is not optional; it is what makes delegation safe.** Subagent output runs
roughly one factual error per ten claims and an invented number is the cardinal sin here, so every
résumé workflow ends with adversarial agents checking each claim against the journey doc and the
honesty rules — anything unsupported is **cut, not softened** — and you adjudicate the survivors
before a word reaches a file he will paste. A claim that survives unchecked is a defect, not a
result.

**Never delegate the open claims** — the confirm-or-reject list is his alone. No agent resolves the
graph neural network, the four Rocket metrics, the 70–80% consolidation, the 27 ms / P95 16 ms
pairing or the 100,000-concurrent wording. Surface them in every prep artefact; leave the résumé
wording alone.

**⚠ .docx IS THE OUTPUT FORM — 2026-08-27.** *"for resumes, we can create docx. right? wouldn't
that be easier?"* · *"we create .docx file(s) that I can also edit easily."* · *"that's going to be
our form now."* · *"No need of a HTML page or anything."*

```
automation/.venv/bin/python automation/resume_docx.py generate   # DB -> master/Abhisheik_Deo_Resume.docx
automation/.venv/bin/python automation/resume_docx.py verify     # re-open it and prove fidelity
```

- **`jobs_tracker_v2` → `.docx` → he edits in Word.** No HTML in the delivery path, no copy/paste
  sheet, no card. `master/upgrad_resume.html` survives ONLY as the round-trip verification artefact
  proving a parse did not drop a `<strong>`; `resume_docx.py` refuses to write to it.
- **It REFUSES rather than emit a quietly-wrong document** — a missing block, an absent section or
  one `<strong>` that failed to become a bold run is a refusal, not a warning. Its **bold gate
  counts OCCURRENCES, not membership**: 209 database spans are only 182 distinct, and a membership
  test let bold vanish from three of four `Java and Spring Boot` spans and still pass
  (`resume-issues-to-avoid/` rule 9 exactly), so the only detector must not be blind to repeats.
  And **never `run.bold = False`** — it writes an explicit `<w:b w:val="0"/>`, direct formatting
  outranks the style, and 299 of them meant editing *List Bullet* in Word's style pane did nothing;
  bold only when true, so the document stays restyleable.

**⛔ SCOPE — per-seat résumés, 2026-08-27: `.docx` for NEW JOBS ONLY.** *"similar path for workspace
specific resumes as well"* · *"new jobs that is"* · **_"ones we've already applied to - do NOT
change them."_** **Every seat past a pre-send state is frozen** (query `jobs_tracker_v2`; never carry the count here) — no `.docx`, regeneration, migration
or edits; the sent PDFs are the record, and migration 011's trigger makes editing a sent version
raise, so it is enforced rather than remembered. **Wipro is the first real selection**, and every
new seat after it. **A per-seat résumé is a selection with edits** in `resume_versions` /
`resume_version_bullets`, never a copied file: copying is the bug — eight workspace copies of his
career exist (six by an earlier count), all diverged, every one stale silently when the master
changed, the master-level duplication recreated one level down.

**⚠ ARCHITECTURE — THE DATABASE IS THE SOURCE, HTML IS A VIEW. ✅ Started by him 2026-08-27:**
*"remember, you SHOULD be using a DB to store the information"* · *"AND prepare the HTML from that
DB"* · *"starting now, we do that"* · *"from the master resume"* · **_"DB is the source. No more
grepping, etc etc"_**. The shape he set out:

> 1. master resume has it's own bullets in a table · 2. you retrieve them, compare them to the JD ·
> 3. score & improve · 4. new bullets are stored in the DB again · 5. using these DB bullets, you
> export the PDF from upgrad · 6. **I only see the final PDF. if any changes are needed, you can
> make those changes to the DB** · 7. a HTML page that helps us with comparison, all running from
> the DB · 8. **HTML is no longer static. it's dynamic.**

A hard change of habit:

- **The database is where résumé content LIVES** — bullets, skills, headline, summary, role
  metadata, education, certifications, personal information. Not the file. So
  **`master/upgrad_resume.html` is a GENERATED ARTEFACT** — regenerated on demand, never authored
  or hand-edited; an edit in the file is lost on the next generate. *(It was also what
  `upgrad_apply.py` parsed by section id and pasted via `_paste_html` before export; upGrad is
  retired.)*
- **⛔ STOP GREPPING THE RÉSUMÉ FILES. Query the database** — *"No more grepping, etc etc"*. Which
  bullets carry a number, which leading verbs are taken, what a role claimed for a seat, where a
  metric appears: `SELECT`s, not `grep -o` piped to `wc -l`. Every *Measurement traps* entry came
  from regexing minified HTML; a query cannot mis-count a line, match `p-e**lpa**so` for "LPA", or
  mistake a Mermaid node id for Amazon S3.
- **Scope, so the boundary is never guessed: the MASTER résumé only** — the eight per-seat
  workspace résumés are NOT migrated and stay files until they are; a sent one is never edited.
- **He supplies the MATERIAL, not the markup** — *"i give you the details of master resume, which
  I've already done."* The journey document, the 17 VoltusWave bullets, the confirmations
  (Kubernetes, Terraform, HIPAA, load balancing, high availability), the corrections. He never
  hand-authors HTML; **his review surface is the exported PDF.** ~~He still writes the master by
  hand.~~ *(Superseded.)* Workflows draft, verify and stage paste-ready content; they do not ship
  on his behalf and never touch the Hiration card.
- **This makes the hygiene rules enforceable rather than advisory** — leading-verb uniqueness
  across all ten roles, ≤25 words, at least one bolded fact, no trailing period — and the verb list
  that *"has been wrong before — never trust it, regenerate from the file"* becomes a constraint.

**⛔ THE GATE IS THE ROUND TRIP, AND IT IS NOT OPTIONAL.** Load the master into the database,
regenerate the HTML, diff: **byte-identical, or every difference enumerated and justified.** A parse
that silently drops a `<strong>` corrupts the master and would not surface until an exported PDF
lost its bold. **A lossy migration is the worst outcome available; stop rather than proceed** —
until that proof passes for a given source, the FILE stays authoritative for it. **Do not
half-migrate:** a master caught mid-migration across a session boundary is the worst state to
inherit.

**`./todo` coordinates, it never executes.** It answers what is due, blocked and next, and records
status changes with reasons; do not grow it into a task runner. A workflow may finish a task and
report it, but marking it `done` / `parked` / `pushed` / `dropped` goes through `./todo`, and
moving a task out always needs at least one reason.


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

## Status — query it, never read it off this file

**There is no status block in the rulebook.** There was one, dated 2026-08-26, and it went stale
within two days — it claimed four applications sent when the database held seven. It is archived at
`docs/ARCHIVE-status-2026-08-26.md`.

- **What happened** → `jobs_tracker_v2`. The board, the timeline, the scores:
  `psql -d jobs_tracker_v2 -c "select slug, company, status, fit_score, applied_at from applications order by fit_score desc nulls last;"`
- **Where we were** → `RESUME_SESSION.md`, rewritten whenever the picture changes materially.
- **What is claimed** → the résumé files and the honesty rules above.

The durable *rules* stay in this file. The durable *facts* live in the database, and a snapshot of
them here is a second source that can only drift.
