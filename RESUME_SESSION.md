# RESUME_SESSION.md

**READ THIS FIRST.** What was in flight when the last context cleared, and what to pick up.
Rewrite it whenever the picture changes materially. Overwrite freely — git carries the history.

**Last rewritten: 2026-08-28 ~00:30.**

**Also read:** `CLAUDE.md` (the rulebook — heavily updated 27 Aug) · `PENDING.md` (the internal
verification record and workflow run IDs) · `db/README.md`.

---

## ⚠ THE PIPELINE CHANGED COMPLETELY ON 27 AUGUST. DISCARD OLDER MEMORY.

```
jobs_tracker_v2  ->  automation/resume_docx.py  ->  .docx  ->  he edits in Word
```

```bash
automation/.venv/bin/python automation/resume_db.py    load|generate|verify
automation/.venv/bin/python automation/resume_docx.py  generate [--slug <seat>]
automation/.venv/bin/python automation/verify_resume_docx.py [file] [--doc-key ...]
```

- **upGrad is RETIRED — his access was revoked.** All eight entry points refuse with exit 3
  (`automation/upgrad_retired.py`). **The files stay on disk**, by his instruction. `cleanup_cards.py`
  still never runs. Do not try to revive it; do not diagnose the refusal as a bug.
- **`.docx` is the output form.** No HTML in the delivery path, no paste sheet, no card.
- **`master/upgrad_resume.html` is NOT a deliverable** — it is the round-trip verification artefact.
  `resume_docx.py` refuses to write to it.
- **The DB is the source for the MASTER ONLY.** The eight per-seat résumés are still files.
- **`.docx` for NEW JOBS ONLY** — *"ones we've already applied to - do NOT change them."*
- ⚠ `master/Abhisheik_Deo_Resume.SUPERSEDED-2026-08-25.pdf` is the last upGrad export and is **WRONG**
  (Knockout.js, 300, no AngularJS/280/Kubernetes). **Never send it.**
- **Always run `verify_resume_docx.py` before handing him a .docx**, and **pass `--doc-key` for a
  per-seat file** or it compares against master's blocks and reports a false pass.

---

## THE BOARD — query it, never read it off filenames

```sql
psql -d jobs_tracker_v2 -c "select slug, company, status, fit_score, applied_at from applications order by fit_score desc nulls last;"
```

**7 applied · 1 BUILT AND UNSENT (Tachyon) · 2 awaiting JD (Wipro, Aezion) · 1 withdrawn.**
Newest: **Tachyon Technologies, AI Architect — Hyderabad, hybrid, built 20 Sep, technical 90.32,
tied top of the board with Keyloop.** Last sent: **Nexifyr, Lead Engineer — FHIR, 78, applied 28 Aug.**

⚠ **The backlog gate is now at 1.** It was 0 this morning. The rule is a judgement call at roughly
five — but the v1 failure was 23 built and unsent, so the number to watch is the trend, not the
threshold.

---

## THE MASTER — rewritten 27 Aug, 39 → 64 bullets

Sourced from `professional-journey-original.md`. 64 distinct leading verbs, zero collisions, zero
bullets over 25 words. Formatted to the reference he supplied: A4, ~0.26in margins, `#328EF7`
accent, `#EBF4FE` bands, **two-line role entries** with a right tab stop:

```
Principal Software Architect            Mar '25 - Apr '26   <- band
VoltusWave Technologies                         Hyderabad   <- no band
```

**Three open claims HE settled on 27 Aug — do not re-ask, do not re-flag:**
- **innRoad = AngularJS**, not Angular. ⚠ AngularJS 1.x is NOT modern Angular; this does not close
  the Angular gaps that docked earlier seats.
- **axe Monitor = 280 clients**, plus ~50 internal instances OUTSIDE the 280. `300+` was FALSE.
  ⚠ **He has NOT stated a total.** 280 + ~50 implies ~330, *higher* than the ~300 he told CBRE —
  so ~300 may have been the instance figure all along. **Ask; never guess.**
- **Aurora PostgreSQL** — settled the platform without needing an edit.

---

## THE JOB WAITING FOR YOU

0. **SEND TACHYON — it is built, verified and unsent.** `September-2026/20/tachyon-ai-architect/`.
   Technical **90.32**, no hard caps. `.docx` verified **35 met / 0 failed**.
   ⚠ **THREE THINGS BEFORE HE CLICKS APPLY:**
   - **There are TWO different "AI Architect" pages on Tachyon's own site.** `/jobs/ai-architect/`
     is a *"Contractual, Long-term"* staff-augmentation placement in **Winchester, Virginia** on
     Salesforce Financial Services Cloud. The Hyderabad full-time seat is `/jobs/ai-architect-2/`.
     Both return HTTP 200 and carry the **identical** page title. The main thread could NOT confirm
     which is which (the content is JavaScript-rendered); the research pass made the attribution.
     **Check the location on the page before applying.**
   - **Open the `.docx` in Word and check it is ≤3 pages.** NOT checkable here — no LibreOffice.
     The seat carries **66 experience bullets** against the master's 64, and the headline grew from
     27 to 32 words, so it may wrap. Cheapest cuts if it spills: the Routed serverless bullet
     (weakest number on the résumé), then "Graph + GNN" from the headline.
   - Apply lands in **Oorwin** (`tachyonind.oorwin.ai`), requisition **TYI-4328**. Single-page form,
     no account needed.

1. **Send the Aezion reply.** `August-2026/31/aezion-inbound-sravan/reply.html`, one copy button,
   70 words. Sravan K Chelimalla emailed cold on 31 Aug naming **no role, no level, no location and
   no stack** — so there is **no technical score**, and that is a recorded absence, not an oversight.
   The reply deliberately **asks him nothing**, not even for the job description: he had already read
   the LinkedIn profile and quoted it back, so the evidence recitation was cut and everything moved to
   the call. Offers **Wed 2 Sep**, 11am–6pm IST, with the number. `research.html` carries the verdict,
   the flags and thirteen forcing questions.
   ⚠ **Two things from that research to carry into the room.** Aezion sells **dedicated offshore
   teams and build-operate-transfer** (its Global Capability Centers line), so "architect" there may
   mean an *engagement* architect on a client account — ask which in the first eight minutes. And
   **Spring Boot appears nowhere on their site**; their only genuinely senior seat is a .NET architect
   role naming Azure and Kafka, both never-claim items.
2. **He opens the .docx in Word.** Three things no gate here can see: **the page count** (never
   verified at 64 bullets; no LibreOffice on this machine), the **band running continuous across the
   tab gap**, and **bold rendering heavier**. If it spills past 3 pages, the ranked cut list is in
   `PENDING.md` — vp#2 and the second statistics bullet are the two free ones.
3. **The freeze gap — real exposure, 7 seats sent.** Migration 011's trigger guards
   `resume_version_bullets`, but the `.docx` path uses `resume_documents`/`resume_blocks` and
   `resume_versions` holds **zero rows**. Nothing stops `resume_db.py load --slug <a-sent-seat>`
   overwriting a résumé that has gone out. On the board as `freeze-sent-resumes`.
4. **Four structural findings on the master, his call, none acted on:** the **VoltusWave return is
   never explained** (he appears to go Co-Founder & VP → Principal Architect at the same company —
   six words in the summary closes it) · the screener's window is all chat platform while Kubernetes
   sits at bullet 23 · **Deque reads as generic SaaS** — `accessib` appears once in five years ·
   the summary's first eight words restate the headline.

⚠ **`source-ic` is still on the board and CONTRADICTS CLAUDE.md**, which says *"Do not source seats…
Wait for the paste."* Left in place deliberately — resolving it is his call, not ours.

---

## NEW SINCE 28 AUG — per-seat résumés now have a re-runnable path

**`db/operations/clone_seat_resume.sql`** starts a per-seat résumé as a **selection with edits** off
the master: it copies every master row into `doc_key='seat:<slug>'` across `resume_documents`,
`resume_roles`, `resume_sections`, `resume_blocks`, `resume_education`, `resume_certifications` and
`resume_profile`. The Nexifyr seat document was created ad hoc and left no record of how; this closes
that. **All three refusals are proven**: re-cloning an existing seat, an unknown slug, and — the one
that matters — **a seat whose application has already been sent**. That last one closes part of the
freeze gap for the clone path, though `resume_db.py load` is still unguarded.

**`db/seats/<slug>.sql`** then carries that seat's Rule 7 tailoring as reviewable, re-runnable SQL,
with the rationale and the source quote for every edit in its header comment. It refuses if the seat
document does not exist or if the application has already been sent, and it **proves itself before
committing** — 0 duplicate leading verbs, 0 bullets over 25 words, 0 `orchestrat` stem collisions.

Two gotchas both scripts now handle, learned the hard way:
- `resume_profile.value_text` is a **generated column** — never insert into it.
- `ord` is part of `resume_blocks`' primary key, so a re-order must **shift the whole section clear
  of the target range first**; assigning 1..N directly collides with rows still holding those ords.

⚠ **`resume_docx.py` refuses unknown HTML entities** (`&middot;` was rejected). The master uses the
literal `·` character. That refusal is correct behaviour, not a bug.

⚠ **`August-2026/27/nexifyr-lead-engineer-fhir/score.json` names the WRONG SEAT inside it** —
`"slug": "adhd-autism-founding-engineer"`. Checked all nine `score.json` files: the other seven
simply **omit** the `slug` key, which is the normal shape, so Nexifyr is the only wrong one.
It is **cosmetic, not functional** — `jobs_sync.py` keys off the directory, and Nexifyr's 78 synced
correctly. Pre-existing, not touched, flagged for him.

---

## RULES THAT BIND EVERY BUILD

- **COMPENSATION IS DEFERRED** until a company reaches that stage. **INTERVIEW PREP WAITS** until
  one responds, then for that seat only.
- **NEVER CLAIM:** Kafka, NATS, MongoDB, ClickHouse, Azure, GCP, SOC 2, Spring Cloud/WebFlux/Batch,
  Grafana, Prometheus, Hazelcast — **and FHIR/HL7/DICOM**, which are zero across every source.
- **Spring Boot is six years across TWO employers with a five-month gap** — never "six continuous".
- **Production Python is ~14 MONTHS.** No rewrite closes it.
- **No Amura outcome metrics exist.** KQ2's table (412/217/0.58/0.34/+24pp/0.08) is NEVER an outcome.
  Amura names no broker; the Kinesis/HA work is the chat platform.
- **UNVERIFIED stays, FALSE comes off.** Say which before proposing any removal.
- **Every pasted JD gets the full build**, no re-asking. **Always ask for the URL.**

---

## MEASUREMENT TRAPS — every one cost real time

`grep -c` counts LINES, not occurrences, and these files are minified — use `grep -o | wc -l`. A
word counter must ignore punctuation tokens. **Check the tool before believing the finding:** on
27 Aug my own bullet-list check flagged a *correct* file as broken, my hygiene checker reported 1
failure where there were 18, and a `.docx` bold gate counted membership instead of occurrences so 27
bold spans were invisible to it. **Adjudicate the verifier too.**
