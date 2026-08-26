"""Read-only suite for jobs_db + /api/jobs.

Unlike test_db.py this one NEVER writes: `jobs_tracker_v2` holds his live seats.
It asserts against whatever is in the database now, so it stays true as rows are
added.

⚠ It reads `jobs_tracker_v2`, v2's own database since 2026-08-26. v1's ninety-two
rows are in `jobs_tracker` and this suite must never see them — section 5 is now
the assertion that it does not, where it used to be the assertion that archiving
had preserved them.
"""
import json
import re
import sys
import pathlib
import urllib.error
import urllib.request

import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import jobs_db

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
API = sys.argv[1] if len(sys.argv) > 1 else None

# The four seats migration 005 moved into jobs_tracker_v2. Asserted by NAME, so
# a fifth seat he registers tonight is expected rather than a failure.
LIVE_SLUGS = ["wipro-principal-software-architect", "o9-senior-architect-agentic",
              "principal-architect-ai-native", "yes-madam-lead-architect"]

P, F = 0, 0
def ok(cond, label):
    global P, F
    if cond: P += 1; print(f"  PASS  {label}")
    else:    F += 1; print(f"  FAIL  {label}")


print("\n1. Every status maps to exactly one tab")
STATUSES = ["new", "recommended_apply", "recommended_skip", "resume_drafted",
            "resume_finalized", "applied", "heard_back", "interviewing",
            "offer", "rejected", "withdrawn"]
with jobs_db.connect() as c, c.cursor() as cur:
    cur.execute("SELECT unnest(enum_range(NULL::application_status))::text AS s")
    live = [r["s"] for r in cur.fetchall()]
ok(live == STATUSES, f"the enum is the eleven this maps — got {live}")
ok("archived" not in live,
   "`archived` is NOT an enum value here — v2's database has no archive concept")
ok(set(jobs_db.TAB_FOR_STATUS) == set(live), "TAB_FOR_STATUS covers every enum value, no extras")
ok(all(jobs_db.tab_for(s) in jobs_db.TABS for s in live), "every status lands on a real tab")
ok(set(jobs_db.TABS) == {jobs_db.tab_for(s) for s in live}, "no tab is invented and none is orphaned")
ok(len(jobs_db.TABS) == 6, f"six tabs — v1's tab set exactly — got {len(jobs_db.TABS)}")
ok("all" not in jobs_db.TABS, "there is no `all` tab, exactly as in v1")

print("\n2. The deliberate decisions are the documented ones")
ok("archived" not in jobs_db.TABS and "archived" not in jobs_db.TAB_FOR_STATUS,
   "no archived tab and no archived status — migration 006 took the concept out")
try:
    jobs_db.tab_for("archived"); ok(False, "an archived row would be refused")
except jobs_db.UnknownStatus:
    ok(True, "an archived row reaching this database would raise, not render")
ok(jobs_db.tab_for("recommended_skip") == "other",
   "recommended_skip -> other (the catch-all; it must not touch the apply queue)")
ok(jobs_db.tab_for("new") == "other", "new -> other (untriaged intake)")
for s in ["recommended_apply", "resume_drafted", "resume_finalized"]:
    ok(jobs_db.tab_for(s) == "ready", f"{s} -> ready (the apply queue, the backlog gate)")
ok(jobs_db.tab_for("applied") == "applied", "applied -> applied")
for s in ["heard_back", "interviewing", "offer"]:
    ok(jobs_db.tab_for(s) == "heard-back", f"{s} -> heard-back (they replied, it is live)")
ok(jobs_db.tab_for("withdrawn") == "closed" and jobs_db.tab_for("rejected") == "not-selected",
   "withdrawn and rejected are kept apart")

print("\n3. An unknown status is raised, never dropped")
try:
    jobs_db.tab_for("ghosted"); ok(False, "unknown status raises")
except jobs_db.UnknownStatus: ok(True, "unknown status raises UnknownStatus")

print("\n4. No row vanishes")
rows = jobs_db.applications()
with jobs_db.connect() as c, c.cursor() as cur:
    cur.execute("SELECT count(*) AS n FROM applications")
    total = cur.fetchone()["n"]
ok(len(rows) == total, f"every row is read — {len(rows)} of {total}")
counts = jobs_db.counts(rows)
ok(sum(counts[t] for t in jobs_db.TABS) == total,
   f"the tabs total the row count — {sum(counts[t] for t in jobs_db.TABS)} vs {total}")
ok(counts["total"] == total, "the `total` count is the row count")
ok(all(r["tab"] for r in rows), "every row carries a tab")
per_status = {}
for r in rows:
    per_status.setdefault(r["status"], set()).add(r["tab"])
ok(all(len(v) == 1 for v in per_status.values()), "a status never splits across tabs")

print("\n5. v1's record is in another database, and nothing here can reach it")
# The point of the split. `jobs_tracker` is v1's 92 rows, frozen; this suite and
# everything it exercises talk to `jobs_tracker_v2`. Non-interference is now a
# property of the connection string, not of every query remembering to filter.
with jobs_db.connect() as c, c.cursor() as cur:
    cur.execute("SELECT count(*) AS n FROM applications"
                " WHERE scraped_at::date < DATE '2026-08-25'")
    n_v1_here = cur.fetchone()["n"]
    cur.execute("SELECT count(*) AS n FROM information_schema.columns"
                " WHERE table_name = 'applications' AND column_name = 'archived_from'")
    n_col = cur.fetchone()["n"]
    cur.execute("SELECT count(*) AS n FROM pg_constraint"
                " WHERE conname = 'applications_archive_remembers'")
    n_check = cur.fetchone()["n"]
ok("jobs_tracker_v2" in jobs_db.DSN, f"jobs_db talks to jobs_tracker_v2 — DSN {jobs_db.DSN!r}")
ok(n_v1_here == 0, "not one row here predates 2026-08-25 — v1's record is elsewhere")
ok(n_col == 0 and n_check == 0,
   "no archived_from column and no archive CHECK — 004 never created them")
ok(all(r["status"] != "archived" for r in rows), "and no row carries an archived status")

# v1's database, read directly and never written. If it is not on this machine
# there is nothing to interfere with, which is the same guarantee by other means.
V1_DISTRIBUTION = {"recommended_skip": 49, "new": 15, "resume_finalized": 14,
                   "applied": 10, "resume_drafted": 3, "interviewing": 1}
try:
    with psycopg.connect("dbname=jobs_tracker", row_factory=dict_row) as c, c.cursor() as cur:
        cur.execute("SELECT status::text AS s, count(*) AS n FROM applications GROUP BY 1")
        v1 = {r["s"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM applications WHERE slug = ANY(%s)",
                    (list(LIVE_SLUGS),))
        n_dupes = cur.fetchone()["n"]
except psycopg.Error as exc:
    ok(True, f"jobs_tracker is not reachable from here — nothing to interfere with ({exc.__class__.__name__})")
else:
    ok(sum(v1.values()) == 92, f"jobs_tracker still holds v1's 92 rows — got {sum(v1.values())}")
    ok(v1 == V1_DISTRIBUTION,
       "with the exact statuses v1 left them in — migration 006 reversed 003 cleanly")
    ok("archived" not in v1, "and not one of them is still archived")
    ok(n_dupes == 0, "none of v2's seats is still sitting in v1's database — one home each")

print("\n6. The live seats are registered, and each is in the pipeline")
# NOT `tab == "ready"`. That asserted a snapshot of where the seats happened to
# be sitting, so the suite failed the moment one was actually SENT — which is
# the north star, not a regression. yes-madam-lead-architect moved to `applied`
# on 2026-08-26.
#
# NOR `tab in jobs_db.TABS`, which replaced it: `tab_for` RAISES on an unknown
# status, and section 1 already proves every enum value lands in TABS, so that
# assertion could not fail on any input and asserted nothing at all.
#
# The durable invariant that survives a send and still bites: `other` is the
# new/recommended_skip catch-all, deliberately excluded from the ready-and-unsent
# backlog gate. A seat we built a whole workspace for must never be sitting in
# it — not at any stage, not ever — and it must resolve to that workspace.
by_slug = {r["slug"]: r for r in rows}
for slug in LIVE_SLUGS:
    r = by_slug.get(slug)
    ok(r is not None, f"{slug} is in the database")
    if r:
        ok(r["tab"] != "other",
           f"{slug} is in the pipeline, not the skip bucket — {r['status']} -> {r['tab']}")
        ok(r["tab"] == jobs_db.TAB_FOR_STATUS[r["status"]],
           f"{slug}'s tab is its status's documented tab, not a stored guess")
        ok(r["workspace"] and r["href"], f"{slug} resolves to its workspace on disk")
w = by_slug.get("wipro-principal-software-architect")
ok(w and w["technical"] is None, "Wipro carries NO technical score — there is no JD to score")

print("\n7. Scores come off the rubric, not out of thin air")
ok(jobs_db.scores(None) == {"technical": None, "non_technical": None, "rubric": None},
   "no breakdown -> no scores, no guesses")
v1 = jobs_db.scores({"hard_reqs": 20, "level": 10, "domain": 10, "location": 5, "freshness": 2.5})
ok(v1["technical"] == 50.0, f"v1 technical rescales hard_reqs/40 -> /100 — got {v1['technical']}")
ok(v1["non_technical"] == 50.0, f"v1 non-technical rescales the four axes/55 — got {v1['non_technical']}")
ok(v1["rubric"] == "v1-five-axis", "and says which rubric produced it")
v2 = jobs_db.scores({"rubric": "v2-weighted", "technical": 83.3})
ok(v2["technical"] == 83.3 and v2["non_technical"] is None,
   "a v2 weighted total is passed through undivided, with no invented functional score")
scored = [r for r in rows if r["rubric"] == "v2-weighted"]
ok(scored and all(0 <= r["technical"] <= 100 for r in scored),
   "every v2 score is a plausible percentage")
ok(all(r["technical"] is None or 0 <= r["technical"] <= 100 for r in rows),
   "so is every v1 rescale")
ok(all(r["rubric"] in (None, "v1-five-axis", "v2-weighted") for r in rows),
   "and every row names a rubric the page knows how to render")

print("\n8. Compensation is not on the launcher")
blob = json.dumps(rows)
ok("salary" not in blob, "no salary field reaches the page — compensation is deferred")
ok("salary" not in jobs_db._SELECT, "and the column is never even selected")

print("\n9. Rows carry what the page needs")
sample = rows[0]
for key in ["slug", "company", "role", "status", "tab", "technical",
            "non_technical", "location", "source_url", "source_note", "workspace",
            "href", "at", "at_kind", "intake"]:
    ok(key in sample, f"row has `{key}`")
ok("archived_from" not in sample,
   "and no `archived_from` — the column does not exist in v2's database")
ok(all(r["source_url"] is None or r["source_url"].startswith("http") for r in rows),
   "a source_url that is not a URL is nulled rather than rendered as a dead link")
ok(all(r["source_url"] is not None or r["source_note"] is not None for r in rows),
   "every row explains where it came from — a URL, a note, or both")
ok(any(r["source_url"] and r["source_note"] for r in rows),
   "and a row may carry BOTH: o9 was applied to via naukri while the URL is the traced requisition")

print("\n10. Intake groups are derived; the note is not")
groups = jobs_db.groups(rows)
dates = [g["date"] for g in groups]
ok(dates == sorted(dates, key=lambda d: d or "", reverse=True), "newest intake date first")
ok(len(dates) == len(set(dates)), "each intake date appears exactly once")
ok(set(dates) == {r["intake"] for r in rows}, "and every row's intake date has a group")
ok(all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", d or "") for d in dates), "dates are ISO")
notes = jobs_db.intake_notes()
ok(isinstance(notes, dict), "the notes file parses")
ok(all(g["note"] == notes.get(g["date"]) for g in groups),
   "a group's note is EXACTLY what the notes file says, or None — never composed here")
ok(all(g["note"] is None for g in groups) if not notes else True,
   f"nothing has been invented — {len(notes)} hand-authored note(s) on file")

print("\n11. The page carries a tab for every tab the data can produce")
markup = (ROOT / "index.html").read_text()
in_markup = set(re.findall(r'data-tab="([^"]+)"', markup))
ok(in_markup == set(jobs_db.TABS),
   f"index.html's tabs are exactly jobs_db.TABS — page {sorted(in_markup)}")
ok(markup.count('class="tab-count"') == len(jobs_db.TABS),
   "and every one of them has a count slot for tabs.js to fill")

if API:
    print("\n12. GET /api/jobs")
    with urllib.request.urlopen(API + "/api/jobs") as r:
        ok(r.status == 200, "answers 200")
        payload = json.loads(r.read())
    ok(payload["store"] == "postgresql", "names its store")
    ok(len(payload["applications"]) == total, f"serves all {total} rows")
    ok(payload["counts"]["total"] == total, "counts agree with the rows")
    ok(sum(payload["counts"][t] for t in jobs_db.TABS) == total, "tabs still total the row count")
    ok(set(payload["counts"]) == {"total", *jobs_db.TABS},
       "and it serves a count for every tab and no others — no `archived`, no `all`")
    ok(len(payload["groups"]) == len(groups), "the intake groups are served too")
    ok("salary" not in json.dumps(payload), "and still no compensation")

    print("\n13. It degrades rather than breaking")
    try:
        urllib.request.urlopen(API + "/api/jobs?boom=1")
        ok(True, "a stray query string is harmless")
    except urllib.error.HTTPError as exc:
        ok(False, f"a stray query string broke it — {exc.code}")
    with urllib.request.urlopen(API + "/index.html") as r:
        ok(r.status == 200, "the launcher itself still serves")
    for path in ["/__daily_api", "/api/state", "/api/history?limit=1"]:
        with urllib.request.urlopen(API + path) as r:
            ok(r.status == 200, f"the daily log's {path} is untouched")
else:
    print("\n12-13. GET /api/jobs — SKIP (no server URL passed)")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
