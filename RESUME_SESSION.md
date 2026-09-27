# RESUME_SESSION.md

**READ THIS FIRST.** What was in flight when the last context cleared, and what to pick up.
Rewrite it whenever the picture changes materially. Overwrite freely — git carries the history.

**Last rewritten: 2026-09-27**, just before he restarted the terminal for a Claude Code update.

**Also read:** `CLAUDE.md` (the rulebook) · `PENDING.md` · `db/README.md`.

---

## FIRST THING: start the server — it was stopped on purpose

`automation/serve.py` was running inside the previous Claude session's shell. He asked for it to be
shut down before the restart, and it was (port 8006 confirmed free). Start it again:

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

As of 27 Sep: **8 applied · 3 awaiting a JD (Wipro 99, Aezion 114, Harshita 121) · 1 withdrawn.**
**Ready-and-unsent backlog: 0.**

- **Tachyon Technologies, AI Architect (116) — APPLIED 24 Sep.** Frozen now: never edit, regenerate
  or re-clone. The 20 Sep build (application 115) was deleted by him with its workspace;
  `db/migrations/013` removed the rows and is pinned to id 115 so a re-run cannot touch 116.
  Rebuilt workspace: `September-2026/24/tachyon-ai-architect/`, technical **91.18** (honest ceiling
  ~92 — Salesforce/SAP/ServiceNow, Azure/GCP and measured outcomes are absent), `.docx` 35/35.
- **Harshita Vishnavam InMail (121) — AI Lead / Architect, Hyderabad, company NOT named.**
  Placeholder slug `harshita-vishnavam-ai-lead-architect` (he asked for the recruiter's name in it).
  `September-2026/27/.../reply.html` stages the reply (available immediately, asks for company + JD,
  proposes **Tue 29 Sep** 11am–1pm or 4–6pm) and the Microsoft Form answers (current city and
  current CTC left for him). **Not yet sent, form not yet filled.** When he says either happened,
  log an `outbound` event. When the JD arrives → full build, same slug unless he renames it.
- **Aezion (114)** — `./todo` still shows *Send the reply to Sravan*, 27 days overdue. Never logged
  as sent. Ask him whether it went, rather than assuming.
- **Wipro (99)** — InMail 25 Aug, still no JD.

---

## HOW A SEAT IS BUILT NOW (worked on 24 Sep, repeat it)

CLAUDE.md **"Resume Writing Points"** (his, 24 Sep): a per-seat `.docx` from the master, edits
**only in the last five roles** (VoltusWave Principal · Deque · Rocket · VoltusWave Co-Founder ·
Teletext), and an HTML page with **one copy block per organisation**.

1. `resume.py new --slug … --url …` (or `--no-url "<reason>"`), save raw JD + card to `job-applications/`,
   log the `inbound` event.
2. `db/operations/clone_seat_resume.sql` → `seat:<slug>`.
3. Phase 1, 4 background agents: `jd.md`/`jd.html` · `research.html` · `score.json` · `proposed_edits.json`.
4. Phase 2, 2 adversarial checkers (quick-vp; the other four roles). Adjudicate here.
5. Write `db/seats/<slug>.sql` from the adjudicated JSON (every UPDATE pinned to the old text and
   RAISES unless it hits exactly 1 row), dry-run with ROLLBACK, apply,
   `resume_docx.py generate --slug`, `verify_resume_docx.py <file> --doc-key seat:<slug>`, `jobs_sync.py`.
6. Phase 3, 2 agents: `index.html` rubric · `resume_changes_for_<N>pct_match.html` (copy blocks
   counted against the DB: bullets and `<strong>` per section).
7. `mark_applied.sql` when he says it went.

---

## OPEN — his call, surfaced, not acted on

- **Master "Reimagined" bullet** claims **PostgreSQL** and **"P95 under 30 ms"** for VoltusWave;
  `professional-journey.md:80` names only DynamoDB + OpenSearch and "30 ms" has zero hits. Confirm or correct.
- **"ELK" is never expanded** in the master — first use is the skills block (quick-skills-ee 16).
- Tachyon questions that carry to future seats: were the **100+ golden queries** actually
  clinician-graded (Instrumented bullet says "built to a contract")? Did he **lead** the
  killer-query sessions with the client's chief executive ("Co-defined" vs "Facilitated")?
- **`db/operations/mark_applied.sql` usage comment is wrong**: it says `-v slug=…` but the script
  reads `current_setting('mark_applied.slug')`. Working call:
  `psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -c "select set_config('mark_applied.slug','<slug>',false)" -f db/operations/mark_applied.sql`.
  He has not said whether to fix the comment.
- `./todo` still carries `journey-doc` (33 days overdue) and the two Aezion tasks.

---

## NOTES THAT ARE ABOUT RUNNING THINGS

- **The "Honesty — load-bearing" section was removed from CLAUDE.md by him on 24 Sep,
  intentionally** ("that was intentional, leave it"). Do not restore it or re-flag its absence.
- `add_breadcrumbs.py` and `expand_acronyms.py` only scan `killer-query-case-studies/`; they never
  check workspace pages. Acronyms on workspace pages depend on the agent that writes them.
- `ord` is part of `resume_blocks`' primary key: shift a section clear (ord + 1000) before renumbering.
- Always pass `--doc-key` to `verify_resume_docx.py` for a per-seat file, or it reports a false pass.
- Page count of a `.docx` is not checkable here (no LibreOffice); he checks it in Word.
- He asks "commit & push ALL" after each piece of work; branch is `qa`.
