# RESUME_SESSION.md

**READ THIS FIRST.** What was in flight when the last context cleared, and what to pick up.
Rewrite it whenever the picture changes materially. Overwrite freely — git carries the history.

**Last rewritten: 2026-09-28, 00:10**, after the Delta referral build.

**Also read:** `CLAUDE.md` (the rulebook) · `PENDING.md` · `db/README.md`.

---

## FIRST THING: is the server running?

`automation/serve.py` runs inside a Claude session's shell and dies with that session.

```bash
lsof -nP -iTCP:8006 -sTCP:LISTEN          # anything listening?
automation/.venv/bin/python automation/serve.py   # http://127.0.0.1:8006/
```

He said it is fine for the server to run in Claude's shell.

---

## THE BOARD — query it, never read it off this file

```sql
psql -d jobs_tracker_v2 -c "select id, slug, status, fit_score, applied_at from applications order by id;"
```

- **Delta Technology and Management Services Pvt. Ltd. (122) — REFERRAL, role to be created,
  status `interviewing` (Heard back tab).** A friend who recently joined referred him; no job
  description; interview with **Kim Batcheler** (UK; Delta's own site headed his page "CEO", but he is
  not a statutory director in India — the Chebrolu family are) **not booked yet**. Friend not named.
  - **Delta is rebranding as Enhansd** — footer *"ENHANSD [FORMERLY DELTA TECHNOLOGY AND MANAGEMENT
    SERVICES PVT. LTD.] - 2026"*; arms Tech "Your People Partner" (live), Studio "Your AI Partner" and
    Apps "Your Enterprise Partner" (not active). deltaintech.com returns HTTP 503.
  - Workspace `September-2026/27/delta-technology-referral/`: **done** — `research.html` (cited; full
    width via the new `.page.full` class), `index.html`, `jd.md`.
  - Prep: `~/Documents/interview-prep/study-plans/delta-technology-referral/` —
    `understanding_kim_and_delta.html` (55 diagrams), `your_stories_for_kim.html` (56 diagrams),
    `index.html`, one link in that repo's root `index.html`. The stories page was checked by three
    adversarial checkers and had 47 rulings applied. **He chose "finish, then stop": no more checking
    rounds.** Commit and push that repo once the fix pass has landed; **never deploy it**.
  - Raw inputs: `job-applications/September-2026/27/delta-technology-referral-*`. Event 45 = his referral note.
- **Harshita Vishnavam (121) — APPLIED 27 Sep via her Microsoft Form** (event 44). A short follow-up
  reply is staged in `reply.html` (form submitted, available immediately, call anytime) — **NOT SENT**.
  When he sends it, log an `outbound` event with the text. **Open, his call:** if a JD ever arrives,
  the seat is applied and therefore frozen — does it still get a tailored résumé?
- **Tachyon (116)** — applied 24 Sep, frozen.
- **Aezion (114)** — ask whether the Sravan reply went; never assume.
- **Wipro (99)** — InMail 25 Aug, still no JD.

---

## OPEN — his call, surfaced, not acted on

- **Publishing the Delta prep folder.** It is not in interview-prep's `.assetsignore`, so the next
  deploy would publish research about a named private person (noindex). Ask before any deploy.
- **Questions only he can settle** (listed in section 9 of `your_stories_for_kim.html`): the graph neural
  network (served or not); Kinesis on-demand vs a shard number he chose; **MySQL** — journey l.383 (Cura
  2015) and l.526 (axe Monitor supported MySQL through Feb 2025) against the prep repo's never-claim list;
  whether the "~300" he once told CBRE was the instance count (his settled figure is **280 axe Monitor
  clients**, 27 Aug); the Voltuswave ↔ Amura relationship in one sentence; Keycloak "zero disruption"
  (confirmed in the journey, unconfirmed in the ledger); Redis in the KQ10 case study's stack.
- **Master "Reimagined" bullet** claims **PostgreSQL** and **"P95 under 30 ms"**; the interview-prep ledger
  says P95 < 30 ms belongs to the DynamoDB write path and must never be attached to PostgreSQL.
- **Kubernetes — the two repos disagree.** This `CLAUDE.md` lists it among his confirmations; the
  interview-prep honesty ledger lists it as never-claim (the record is ECS Fargate).
- **"ELK" is never expanded** in the master — first use is the skills block (quick-skills-ee 16).
- Tachyon questions that carry to future seats: were the **100+ golden queries** clinician-graded?
  Did he **lead** the killer-query sessions ("Co-defined" vs "Facilitated")?
- **`db/operations/mark_applied.sql` usage comment is wrong** (`-v slug=…`); the working call is
  `psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('mark_applied.slug','<slug>',false)" -f db/operations/mark_applied.sql`.
- **Pre-existing CSS bug, not fixed:** on phones `dl.context-grid` never folds to one column — the 720px
  rule `.context-grid` loses to the more specific base rule `dl.context-grid`. Shared rule; his call.
- `./todo` still carries `journey-doc` and the two Aezion tasks.

---

## NEW THIS SESSION

- `db/operations/set_status.sql` — any status move except `applied` / `withdrawn` (those keep their
  own scripts); a note is required; the usage comment in its header is correct:
  `psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('set_status.slug','<slug>',false), set_config('set_status.status','<status>',false), set_config('set_status.note','<reason>',false)" -f db/operations/set_status.sql`
- `style.css` — `.page.full` / `.wrap.full`: no width cap, and lifts the prose caps inside it. Only the
  Delta `research.html` uses it.
- **The web-search budget is 200 per session** (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`). The Delta
  research used all of it; later research in the same session could only fetch pages (curl works).
- Messages with apostrophes or quotes: write the `set_config` select to a scratch `.sql` file with
  dollar-quoting, then `psql -f that.sql -f db/operations/log_event.sql`. Shell quoting mangles them.
- **Pace:** the Delta build took ~2h15m and he said *"It's been ages. really ages."* Two prep pages of
  35–40K words and 55 diagrams each were far too big for one interview; size prep to the round.

---

## NOTES THAT ARE ABOUT RUNNING THINGS

- **The "Honesty — load-bearing" section was removed from CLAUDE.md by him on 24 Sep,
  intentionally.** Do not restore it or re-flag its absence.
- Every workspace needs an `index.html` — the launcher links the directory, and without one he gets
  a bare file listing (he flagged it on Harshita, 27 Sep).
- `add_breadcrumbs.py` and `expand_acronyms.py` only scan `killer-query-case-studies/`.
- `ord` is part of `resume_blocks`' primary key: shift a section clear (ord + 1000) before renumbering.
- Always pass `--doc-key` to `verify_resume_docx.py` for a per-seat file, or it reports a false pass.
- Page count of a `.docx` is not checkable here (no LibreOffice); he checks it in Word.
- He asks "commit & push ALL" after each piece of work; branch is `qa`.
