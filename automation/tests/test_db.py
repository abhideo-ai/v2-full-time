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

reset()
print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
