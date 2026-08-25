#!/bin/bash
# Full test run for the daily log and the launcher. From the repo root:
#
#     bash automation/tests/run.sh
#
# The Python suites need only the venv. The page suites need jsdom:
#
#     npm install jsdom          (creates ./node_modules, gitignored)
#
# ⚠ test_db.py and test_page.js TRUNCATE v2_daily's tables. Never point them at a
# database whose contents matter — they are destructive by design.
#
# test_jobs_db.py and test_launcher.js read jobs_tracker and NEVER write to it:
# it holds v1's ninety-two rows plus the live seats, and losing those is not a
# test failure, it is data loss.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY=automation/.venv/bin/python
FAIL=0

echo "=== database layer (v2_daily — destructive) ==="
$PY automation/tests/test_db.py || FAIL=1

echo; echo "=== jobs layer (jobs_tracker — read-only) ==="
$PY automation/tests/test_jobs_db.py || FAIL=1

if [ ! -d node_modules/jsdom ]; then
  echo; echo "=== page ==="; echo "  SKIP — run 'npm install jsdom' first"
  exit $FAIL
fi

echo; echo "=== page (real server + real database) ==="
# A synthetic second day so the rollover path is exercised; reverted after.
cp daily/days.json /tmp/days.real.$$.json
$PY - <<'PY'
import json; from pathlib import Path
p = Path("daily/days.json"); d = json.loads(p.read_text())
d["days"].append({"date": "2026-08-24", "groups": [{"title": "Yesterday", "kind": "blocking",
  "why": "synthetic test day", "items": [
    {"id": "old-done",    "p": 1, "needs": [],           "task": "Finished yesterday",  "detail": ""},
    {"id": "old-parked",  "p": 1, "needs": [],           "task": "Parked yesterday",    "detail": ""},
    {"id": "old-open",    "p": 1, "needs": [],           "task": "Unfinished yesterday","detail": ""},
    {"id": "old-blocked", "p": 2, "needs": ["old-open"], "task": "Blocked yesterday",   "detail": ""}]}]})
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PY
$PY automation/daily.py >/dev/null
psql -d v2_daily -qc "TRUNCATE task_state, task_event RESTART IDENTITY"
$PY automation/serve.py --port 8106 >/tmp/serve106.$$.log 2>&1 &
python3 -m http.server 8107 --bind 127.0.0.1 >/dev/null 2>&1 &
# 8108: the same server pointed at a database that does not exist, so the
# launcher's 503 path is exercised against a real 503 rather than a mock.
JOBS_TRACKER_DSN="dbname=jobs_tracker_no_such_database" \
  $PY automation/serve.py --port 8108 >/tmp/serve108.$$.log 2>&1 &
sleep 2
node automation/tests/test_page.js || FAIL=1

echo; echo "=== jobs layer, over HTTP ==="
# Same suite, now with a server to talk to. Only the HTTP sections are printed —
# sections 1-8 already ran above — but the exit code is the whole suite's.
$PY automation/tests/test_jobs_db.py http://127.0.0.1:8106 >/tmp/jobsapi.$$.log 2>&1 || FAIL=1
sed -n '/^9\. GET/,$p' /tmp/jobsapi.$$.log; rm -f /tmp/jobsapi.$$.log

echo; echo "=== launcher (real server + real jobs_tracker) ==="
node automation/tests/test_launcher.js \
  http://127.0.0.1:8106 http://127.0.0.1:8107 http://127.0.0.1:8108 || FAIL=1

pkill -f "serve.py --port 8106"; pkill -f "http.server 8107"
pkill -f "serve.py --port 8108"

cp /tmp/days.real.$$.json daily/days.json && rm -f /tmp/days.real.$$.json
$PY automation/daily.py >/dev/null
psql -d v2_daily -qc "TRUNCATE task_state, task_event RESTART IDENTITY" >/dev/null
echo; [ $FAIL -eq 0 ] && echo "ALL SUITES PASSED" || echo "FAILURES — see above"
exit $FAIL
