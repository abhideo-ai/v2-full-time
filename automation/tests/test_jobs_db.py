"""Read-only suite for jobs_db + /api/jobs.

Unlike test_db.py this one NEVER writes: `jobs_tracker` holds v1's real record
and the four live seats. It asserts against whatever is in the database now, so
it stays true as rows are added.
"""
import json
import sys
import pathlib
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import jobs_db

API = sys.argv[1] if len(sys.argv) > 1 else None

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
ok(set(jobs_db.TAB_FOR_STATUS) == set(live), "TAB_FOR_STATUS covers every enum value, no extras")
ok(all(jobs_db.tab_for(s) in jobs_db.TABS for s in live), "every status lands on a real tab")
ok(len({jobs_db.tab_for(s) for s in live}) <= len(jobs_db.TABS), "no tab is invented")

print("\n2. The deliberate decisions are the documented ones")
ok(jobs_db.tab_for("recommended_skip") == "closed",
   "recommended_skip -> closed (the 49; not parked, not building)")
ok(jobs_db.tab_for("new") == "parked", "new -> parked (untriaged intake, revivable)")
ok(jobs_db.tab_for("resume_finalized") == "ready", "resume_finalized -> ready (the backlog gate)")
ok(jobs_db.tab_for("applied") == "sent", "applied -> sent")
ok(jobs_db.tab_for("offer") == "interviewing", "offer -> interviewing (no offer tab)")
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
ok(counts["all"] == total, "the `all` count is the row count")
ok(all(r["tab"] for r in rows), "every row carries a tab")
per_status = {}
for r in rows:
    per_status.setdefault(r["status"], set()).add(r["tab"])
ok(all(len(v) == 1 for v in per_status.values()), "a status never splits across tabs")

print("\n5. The four v2 seats are registered")
by_slug = {r["slug"]: r for r in rows}
for slug in ["wipro-principal-software-architect", "o9-senior-architect-agentic",
             "principal-architect-ai-native", "yes-madam-lead-architect"]:
    r = by_slug.get(slug)
    ok(r is not None, f"{slug} is in the database")
    if r:
        ok(r["tab"] == "building", f"{slug} shows under building")
        ok(r["workspace"] and r["href"], f"{slug} resolves to its workspace on disk")
w = by_slug.get("wipro-principal-software-architect")
ok(w and w["technical"] is None, "Wipro carries NO technical score — there is no JD to score")

print("\n6. Scores come off the rubric, not out of thin air")
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

print("\n7. Compensation is not on the launcher")
blob = json.dumps(rows)
ok("salary" not in blob, "no salary field reaches the page — compensation is deferred")
ok("salary" not in jobs_db._SELECT, "and the column is never even selected")

print("\n8. Rows carry what the page needs")
sample = rows[0]
for key in ["slug", "company", "role", "status", "tab", "technical", "non_technical",
            "location", "source_url", "workspace", "href", "at", "at_kind"]:
    ok(key in sample, f"row has `{key}`")
ok(all(r["source_url"] is None or r["source_url"].startswith("http") for r in rows),
   "a source_url that is not a URL is nulled rather than rendered as a dead link")

if API:
    print("\n9. GET /api/jobs")
    with urllib.request.urlopen(API + "/api/jobs") as r:
        ok(r.status == 200, "answers 200")
        payload = json.loads(r.read())
    ok(payload["store"] == "postgresql", "names its store")
    ok(len(payload["applications"]) == total, f"serves all {total} rows")
    ok(payload["counts"]["all"] == total, "counts agree with the rows")
    ok(sum(payload["counts"][t] for t in jobs_db.TABS) == total, "tabs still total the row count")
    ok("salary" not in json.dumps(payload), "and still no compensation")

    print("\n10. It degrades rather than breaking")
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
    print("\n9-10. GET /api/jobs — SKIP (no server URL passed)")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
