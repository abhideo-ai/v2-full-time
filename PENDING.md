# PENDING.md — internal verification record, 2026-08-27

Analysis and run IDs that outlive a session. `RESUME_SESSION.md` is the "where were we";
this is the evidence behind it. Written for the next session's benefit, not as a status report.

---

## THE ARTEFACT

`master/Abhisheik_Deo_Resume.docx` — generated from `jobs_tracker_v2` by
`automation/resume_docx.py`, restyled to match the format he supplied
(`master/Abhisheik_Deo_Resume.SUPERSEDED-2026-08-25.docx`).

```
automation/.venv/bin/python automation/resume_docx.py generate   # DB -> .docx
automation/.venv/bin/python automation/verify_resume_docx.py     # 35 requirements
```

**Result: 35 of 35 checkable requirements met, 0 failed, 1 not checkable here.**

---

## WHAT WAS VERIFIED, AND HOW

Requirements accumulated across the day from CLAUDE.md, `resume-issues-to-avoid/`, migration 012
and a dozen of his own decisions. They are now executable in
`automation/verify_resume_docx.py` — spread across four documents and a conversation, "does it meet
our requirements" was unanswerable.

| group | checks | result |
|---|---|---|
| content vs database | 91 blocks byte-identical; 209 `<strong>` occurrences bold | ✅ |
| settled facts present | AngularJS · 280 · Aurora · Apr 2026 | ✅ |
| stale content absent | Knockout · `Product & Platform Strategy` · `300+` · bare `Angular` | ✅ |
| hygiene | 0 over 25 words · 0 trailing periods · 64 distinct verbs · 0 banned tech | ✅ |
| ATS safety | 0 tables · 0 text boxes · 0 images · single column · real list numbering | ✅ |
| editability | 0 `w:b w:val="0"` · built-in style names · docProps stamped | ✅ |
| format vs his reference | A4 · margins `367/390/484/397` exact · `#328EF7` · `EBF4FE` bands | ✅ |
| **3 pages or fewer** | **NOT CHECKABLE — no LibreOffice; only prior export was 39 bullets** | ⏸ |

**The bold check counts OCCURRENCES, not membership.** 209 spans, only 182 distinct. A membership
test let bold vanish from three of the four `Java and Spring Boot` spans and still passed — proven
by sabotage, which the corrected gate catches as `want 4, have 1`.

---

## WORKFLOW RUN IDS

| run | what | agents | outcome |
|---|---|---|---|
| `wf_2666c1e5-11a` | settle AngularJS / 280 / Aurora across the master | 12 | 5 edits shipped, 2 dropped by verifiers |
| `wf_4677ee39-7db` | DB-as-source migration | 9 (3 died — machine slept) | round trip byte-identical; 2 HIGH bugs found |
| `wf_2b3255fd-766` | first .docx generator | 9 | all 4 verifiers DEFECTIVE; 5 blocking fixes |
| `wf_d1485491-449` | restyle to his format | 8 | 1 blocking defect (Education); fixed |
| `wjd09im0t` | Word paste sheet | — | **killed** — superseded by .docx |

---

## WHAT THE ADVERSARIAL PANELS CAUGHT THAT I DID NOT

Recorded because the pattern matters more than the instances: **every panel found something real,
and three of the findings were in my own verification tooling rather than in the artefact.**

- `verify` in `resume_db.py` **silently destroyed database edits** and its "BYTE-IDENTICAL" was a
  tautology that could not fail — it loaded the file, then compared the render against that file.
- A **retired bullet was permanently deleted by the next `load`**, the feature quietly destroying
  the thing it existed to preserve. My first fix then violated `UNIQUE (doc_key, bullet_key)` and
  **rolled back the whole transaction while `load` still printed success.**
- The .docx **bold gate counted membership, not multiplicity** — 27 occurrences invisible.
- **1.15 line spacing** from python-docx's `docDefaults` applied to all 112 paragraphs, costing
  ~half a page, silently defeating the deliberate spacing.
- **299 `<w:b w:val="0"/>`** direct-formatting overrides made Word's style pane useless.
- `jobs_sync.py` used `len(text.split())` — the counter CLAUDE.md names by name — disagreeing with
  the correct one on **34 of 91 bullets**.

### My own errors, recorded deliberately

- I stripped `3 fronts` from an innRoad bullet as "filler" and removed its only scale marker. The
  drafting agent was right; I restored it.
- My `hygiene_check.py` reported **1 failure where there were 18** — no acronym-expansion check at
  all, and an `[A-Z]{2,}` pattern blind to `SaaS`/`APIs`/`ASP.NET`.
- My first bullet-list check flagged a **correct** file as broken: it demanded inline `<w:numPr>`,
  but the file gets bullets from the `ListBullet` **style**, which is the better form.
- I over-corrected the acronym-expansion detector so that mere membership of a parenthetical
  counted as an expansion, which wrongly cleared `ISO`.

**A verification report listing only passes would have been worth very little.**

---

## THE FORMAT: WHAT WAS DELIBERATELY NOT COPIED

His reference is a **PDF→Word conversion and its structure is broken** — verified, not assumed:

- `HIPAA, ISO 27001 · AI-Leveraged Delivery (Claude Code + OpenAI Codex) SUMMARY` — the headline's
  tail merged into the SUMMARY heading, one paragraph.
- `Cross-Functional Leadership & Stakeholder Alignment Engineering Excellence` — a skills item run
  into the next group's title.
- Two **layout tables** (one wrapping the whole innRoad role) and an embedded `image1.jpg`.
- Its content is stale: Knockout.js, `Product & Platform Strategy`, the pre-rewrite skills.

Taken: colour, bands, margins, sizes, rules, bullet geometry. **Not taken:** merged paragraphs,
layout tables, the image, justified body. A naive ATS parse of his reference yields
`Deque Software\tHyderabad` with **no title and no dates**; the generated file does not.

---

## OPEN — HIS CALL, NOT OURS

1. **Page count.** Never verified at 64 bullets. If it spills to 4, the ranked cut list is in the
   26 Aug review: vp#2 (fully subsumed by vp#3) and the second statistics bullet
   (`match_manifest_id` is the artefact the bullet above it produces) are the two free ones.
2. **The VoltusWave return is unexplained** — on the page he goes Co-Founder & VP → Principal
   Architect at the same company. Six words in the summary closes it. Largest narrative hole.
3. **~330 vs ~300.** 280 clients + ~50 internal implies ~330 instances, *higher* than the ~300 he
   told CBRE. No total is written anywhere. Ask; never guess.
4. **Confirm-or-reject, untouched as required:** the four Rocket metrics, the 70–80%, the
   100,000-concurrent wording, where the +65% attaches, whether the LLM guardrails shipped.
5. Front-loading, Deque's invisible accessibility domain, the summary's duplicated opening.

---

## SCOPE BOUNDARIES IN FORCE

- **DB is the source — MASTER ONLY.** The eight per-seat résumés are still files.
- **.docx for NEW JOBS ONLY.** The seven sent/withdrawn seats are frozen: no .docx, no
  regeneration, no edits. Verified all seven last modified 26 Aug, untouched through 27 Aug.
  Migration 011's trigger makes editing a sent version raise.
- **upGrad is retired** — access revoked; all eight entry points refuse with exit 3.
- `master/upgrad_resume.html` is **not a deliverable** — it is the round-trip verification artefact,
  and `resume_docx.py` refuses to write to it.
