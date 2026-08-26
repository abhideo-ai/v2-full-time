import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import db

P, F = 0, 0
def ok(cond, label):
    global P, F
    if cond: P += 1; print(f"  PASS  {label}")
    else:    F += 1; print(f"  FAIL  {label}")

def reset():
    with db.connect() as c, c.cursor() as cur:
        cur.execute("TRUNCATE task_state, task_event RESTART IDENTITY")
        c.commit()

K = "2026-08-25::clone-card"
K2 = "2026-08-25::paste-jds"

print("\n1. done / undone")
reset()
s = db.apply_ops([{"key": K, "action": "done"}])
ok(s["tasks"][K]["done"] is True, "done sets done=true")
ok("done_at" in s["tasks"][K], "done stamps done_at")
s = db.apply_ops([{"key": K, "action": "undone"}])
ok(s["tasks"][K]["done"] is False, "undone clears done")
ok("done_at" not in s["tasks"][K], "undone clears done_at")

print("\n2. park / push / drop / restore")
reset()
s = db.apply_ops([{"key": K2, "action": "parked",
                   "reasons": ["posting-closed", "comp-below"],
                   "note": "role pulled from their careers page"}])
ok(s["tasks"][K2]["moved"] == "parked", "parked recorded")
ok(s["tasks"][K2]["reasons"] == ["posting-closed", "comp-below"], "SEVERAL reasons stored, in order")
ok(s["tasks"][K2]["note"].startswith("role pulled"), "note stored")
s = db.apply_ops([{"key": K2, "action": "pushed", "until": "2026-08-27", "reasons": ["blocked"]}])
ok(s["tasks"][K2]["moved"] == "pushed" and s["tasks"][K2]["until"] == "2026-08-27", "pushed with return date")
ok("note" not in s["tasks"][K2], "pushed cleared the previous note")
s = db.apply_ops([{"key": K2, "action": "restored"}])
ok("moved" not in s["tasks"][K2], "restored clears the move")
ok("reasons" not in s["tasks"][K2], "restored clears the reasons")
ok("until" not in s["tasks"][K2], "restored clears until")
s = db.apply_ops([{"key": K2, "action": "dropped", "reasons": ["duplicate"]}])
ok(s["tasks"][K2]["moved"] == "dropped", "dropped recorded")

print("\n3. done overrides a move")
reset()
db.apply_ops([{"key": K, "action": "parked", "reasons": ["blocked"]}])
s = db.apply_ops([{"key": K, "action": "done"}])
ok(s["tasks"][K]["done"] is True and "moved" not in s["tasks"][K], "ticking a parked task unparks it")
ok("reasons" not in s["tasks"][K], "and drops the reasons with it")

print("\n4. validation rejects bad ops")
reset()
for label, op in [
    ("pushed with no until",   {"key": K, "action": "pushed", "reasons": ["blocked"]}),
    ("park with NO reasons",   {"key": K, "action": "parked"}),
    ("park with an EMPTY list",{"key": K, "action": "parked", "reasons": []}),
    ("park with a blank reason",{"key": K, "action": "parked", "reasons": ["  "]}),
    ("park with a non-string", {"key": K, "action": "parked", "reasons": [7]}),
    ("park with duplicates",   {"key": K, "action": "parked", "reasons": ["blocked", "blocked"]}),
    ("unknown action",         {"key": K, "action": "yeeted"}),
    ("key with no ::",         {"key": "clone-card", "action": "done"}),
    ("key with a bad date",    {"key": "2026-13-45::x", "action": "done"}),
    ("empty task id",          {"key": "2026-08-25::", "action": "done"}),
    ("bad until format",       {"key": K, "action": "pushed", "until": "next tuesday"}),
]:
    try:
        db.apply_ops([op]); ok(False, f"{label} rejected")
    except db.OpError: ok(True, f"{label} rejected")
try:
    db.apply_ops([]); ok(False, "empty op list rejected")
except db.OpError: ok(True, "empty op list rejected")

print("\n5. one bad op rolls back the whole batch")
reset()
try:
    db.apply_ops([{"key": K, "action": "done"}, {"key": "bogus", "action": "done"}])
except db.OpError: pass
ok(db.get_state()["tasks"] == {}, "no partial write from a batch containing a bad op")

print("\n6. history is append-only and ordered")
reset()
db.apply_ops([{"key": K, "action": "done"}])
db.apply_ops([{"key": K, "action": "undone"}])
db.apply_ops([{"key": K, "action": "parked", "reasons": ["posting-closed", "comp-below"]}])
h = db.history(10)
ok(len(h) == 3, f"three events recorded — got {len(h)}")
ok([e["action"] for e in h] == ["parked", "undone", "done"], f"newest first — got {[e['action'] for e in h]}")
ok(h[0]["reasons"] == ["posting-closed", "comp-below"], "every reason kept in history")

print("\n7. DB constraints hold against direct writes")
reset()
import psycopg
with db.connect() as c, c.cursor() as cur:
    for label, sql in [
        ("key must match day::task_id",
         "INSERT INTO task_state (key, day, task_id) VALUES ('wrong', '2026-08-25', 'clone-card')"),
        ("moved must be a known value",
         "INSERT INTO task_state (key, day, task_id, moved) VALUES ('2026-08-25::x', '2026-08-25', 'x', 'vanished')"),
        ("pushed requires until",
         "INSERT INTO task_state (key, day, task_id, moved, reasons) VALUES ('2026-08-25::y', '2026-08-25', 'y', 'pushed', ARRAY['blocked'])"),
        ("a move REQUIRES at least one reason",
         "INSERT INTO task_state (key, day, task_id, moved) VALUES ('2026-08-25::z', '2026-08-25', 'z', 'parked')"),
        ("an empty reasons array is not a reason",
         "INSERT INTO task_state (key, day, task_id, moved, reasons) VALUES ('2026-08-25::w', '2026-08-25', 'w', 'parked', ARRAY[]::text[])"),
    ]:
        try:
            cur.execute(sql); c.commit(); ok(False, label)
        except psycopg.errors.CheckViolation:
            c.rollback(); ok(True, label)

print("\n8. `./todo` and the board agree on what is on today's list")
# daily_cli.build_view is documented as a mirror of render() in static/todo.js.
# It was not: the board grew a third membership clause (acted on today) and a
# timed Pushed lane, and the CLI kept the old two, so the same database row
# produced two different answers depending on which one you asked.
import daily_cli                                              # noqa: E402
DOC = daily_cli.load_doc()
TODAY = "2026-08-26"                    # a day nothing is authored for
IDS = lambda v: [t["id"] for t in v["current"]]                # noqa: E731

v = daily_cli.build_view(DOC, {"2026-08-25::clone-card":
                               {"done": True, "done_at": f"{TODAY}T09:12:00"}}, TODAY)
ok("clone-card" in IDS(v),
   "a task ticked TODAY stays on the list — rollover refuses to carry it, the third clause keeps it")
ok(v["done_n"] == 1 and v["total_n"] > 1,
   f"and it is counted as done rather than vanishing — got {v['done_n']}/{v['total_n']}")

v = daily_cli.build_view(DOC, {"2026-08-25::source-ic":
                               {"done": False, "moved": "pushed", "until": TODAY,
                                "reasons": ["blocked"], "moved_at": "2026-08-25T20:00:00"}}, TODAY)
ok("source-ic" in IDS(v),
   "a push whose return date has ARRIVED comes back — `push` promises exactly this")
ok(not any(t["id"] == "source-ic" for t in v["moved"] if t["out"]),
   "and it is no longer counted as moved out")
t = next(t for t in v["current"] if t["id"] == "source-ic")
ok("due today" in daily_cli.due_label(t, TODAY),
   f"due against its RETURN date, not its origin day — got {daily_cli.due_label(t, TODAY)!r}")

v = daily_cli.build_view(DOC, {"2026-08-25::source-ic":
                               {"done": False, "moved": "pushed", "until": "2026-09-01",
                                "reasons": ["blocked"], "moved_at": "2026-08-25T20:00:00"}}, TODAY)
ok("source-ic" not in IDS(v), "a push still in the future stays off the list")

for moved in ("parked", "dropped"):
    v = daily_cli.build_view(DOC, {"2026-08-25::paste-jds":
                                   {"done": False, "moved": moved, "reasons": ["blocked"],
                                    "moved_at": "2026-08-25T20:00:00"}}, TODAY)
    ok("paste-jds" not in IDS(v), f"a task {moved} on an earlier day stays off the list")
    ok(any(t["id"] == "paste-jds" for t in v["moved"]), f"and shows in the backlog instead")

ok(daily_cli.on_board({"day": TODAY, "state": {}}, TODAY), "authored for today -> on the list")
ok(not daily_cli.on_board({"day": "2026-08-25", "state": {"done": True,
                           "done_at": "2026-08-25T10:00:00"}}, TODAY),
   "finished on an EARLIER day -> off it, which is what rollover means")

print("\n9. `./todo restore` honours the reasons — one terminal reason closes a task")
# `backlog` already withheld the `./todo restore` hint from a task whose reasons
# are all terminal, and then `restore` brought it back anyway with a cheerful
# tick. The rule was printed and not enforced, in the tool AND on the board.
# db.py deliberately stays out of this: it stores reason KEYS and has no
# vocabulary to judge them by, so the rule lives where days.json is read.
import contextlib                                             # noqa: E402
import io                                                     # noqa: E402


def run_cli(argv: list) -> tuple:
    """Drive the real entry point, so this cannot pass against a private copy."""
    old, buf = sys.argv, io.StringIO()
    sys.argv = ["todo"] + argv
    try:
        with contextlib.redirect_stdout(buf):
            daily_cli.main()
        return 0, buf.getvalue()
    except SystemExit as exc:
        return exc.code, buf.getvalue() + (exc.code if isinstance(exc.code, str) else "")
    finally:
        sys.argv = old


reset()
db.apply_ops([{"key": K2, "action": "parked", "reasons": ["posting-closed"]}])
code, out = run_cli(["restore", "paste-jds"])
ok(code != 0, "restoring a closed-for-good task fails rather than succeeding quietly")
ok("closed for good" in out, "and says so")
ok("Posting no longer active" in out, "naming the reason that closed it, by label")
ok("--reason" in out, "and the way back, so the refusal is not a dead end")
ok(db.get_state()["tasks"][K2]["moved"] == "parked", "nothing was written — it is still parked")

db.apply_ops([{"key": K, "action": "parked", "reasons": ["blocked"]}])
code, out = run_cli(["restore", "clone-card"])
ok(code == 0, "a park whose every reason can come back still restores")
ok("moved" not in db.get_state()["tasks"][K], "and really is back")

# Mixed reasons: one terminal is enough, which is the whole point of `every`.
db.apply_ops([{"key": K, "action": "parked", "reasons": ["blocked", "duplicate"]}])
code, out = run_cli(["restore", "clone-card"])
ok(code != 0, "one terminal reason among revivable ones still closes it")
ok("Already applied" in out and "Blocked on something else" not in out,
   "and only the terminal reason is blamed")

reset()
print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
