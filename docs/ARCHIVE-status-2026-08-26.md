# ARCHIVE — CLAUDE.md Status section, 2026-08-26

Superseded. `RESUME_SESSION.md` is the live "where were we", and `jobs_tracker_v2` is
authoritative for what happened. This snapshot said four applications had been sent; the
database now reads seven applied. Archived out of CLAUDE.md on 2026-09-21 because a stale
status block in the rulebook is worse than no status block.

Query the board instead:

```sql
psql -d jobs_tracker_v2 -c "select slug, company, status, fit_score, applied_at
                              from applications order by fit_score desc nulls last;"
```

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

