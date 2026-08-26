#!/usr/bin/env python3
"""Daily log from the terminal — see what's due, and change status with reasons.

    ./todo                          what's due today
    ./todo done   <task>            tick it
    ./todo undone <task>            untick it
    ./todo park   <task>            park it (asks for reasons)
    ./todo push   <task> --until 2026-08-27
    ./todo drop   <task>
    ./todo restore <task>           bring it back (refused if a reason is terminal)
    ./todo backlog                  what's moved out, and what can come back
    ./todo history [-n 20]

Moving a task out ALWAYS needs at least one reason. Interactively it asks; with
--reason it takes them from the flags; with neither, on a non-tty, it refuses
rather than inventing one. That refusal is the point: it means an agent running
this on your behalf has to come back and ask you.

Which reasons a task carries decides whether it can come back — a task is
revivable only if EVERY one of its reasons is (daily/days.json, `revivable`).
That is enforced, not captioned: `restore` refuses a task carrying a terminal
reason, names the reason, and tells you the way back — record a new move with a
reason that can come back. The board's Restore button refuses identically.

Reads task definitions from daily/days.json and state from PostgreSQL, so it
sees exactly what the page sees. The page's copy of this logic lives in
static/todo.js; the two must agree, and automation/tests cross-checks them.
"""
import argparse
import html as html_mod
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DAYS_JSON = ROOT / "daily" / "days.json"
TTY = sys.stdin.isatty() and sys.stdout.isatty()

C = {"dim": "\033[2m", "red": "\033[31m", "yel": "\033[33m", "grn": "\033[32m",
     "bold": "\033[1m", "off": "\033[0m"} if TTY else dict.fromkeys(
    ["dim", "red", "yel", "grn", "bold", "off"], "")


def plain(markup: str) -> str:
    """Task text is authored as HTML; the terminal wants none of it."""
    return html_mod.unescape(re.sub(r"<[^>]+>", "", markup)).strip()


def load_doc() -> dict:
    doc = json.loads(DAYS_JSON.read_text())
    doc["days"].sort(key=lambda d: d["date"], reverse=True)
    return doc


def revivable_map(doc: dict) -> dict:
    return {r["key"]: bool(r.get("revivable")) for r in doc.get("reasons", [])}


def blocking_reasons(reasons, revive: dict) -> list:
    """The reasons that close a task for good. Empty means it can come back."""
    return [r for r in (reasons or []) if not revive.get(r, True)]


def can_come_back(reasons, revive: dict) -> bool:
    return bool(reasons) and not blocking_reasons(reasons, revive)


def is_out(s: dict, today: str) -> bool:
    moved = s.get("moved")
    if moved in ("parked", "dropped"):
        return True
    return moved == "pushed" and (s.get("until") or "") > today


def acted_today(ts, today: str) -> bool:
    return isinstance(ts, str) and ts[:10] == today


def on_board(t: dict, today: str) -> bool:
    """Mirror of membership() in static/todo.js. Three ways onto today's list.

    The third clause is why this exists at all: a task ticked TODAY but authored
    on an earlier day is not `active` (wrong day) and does not `roll` (rollover
    refuses to carry a finished task forward), so it vanished from `./todo`
    entirely while the page kept it in Done. On a day with nothing authored,
    that was every task he ticked — the count read 0/9 after nine ticks.
    """
    s = t["state"]
    return (t["day"] == today
            or (t["day"] < today and s.get("done") is not True and not is_out(s, today))
            or acted_today(s.get("done_at"), today)
            or acted_today(s.get("moved_at"), today))


def build_view(doc: dict, state: dict, today: str) -> dict:
    """Mirror of render() in static/todo.js. Keep the two in step."""
    days = doc["days"]
    tasks = []
    for day in days:
        for group in day["groups"]:
            for item in group["items"]:
                key = f"{day['date']}::{item['id']}"
                s = state.get(key, {})
                tasks.append({
                    "key": key, "day": day["date"], "id": item["id"],
                    "group": group["title"], "kind": group.get("kind", ""),
                    "text": plain(item["task"]), "p": item.get("p", 2),
                    "due": item.get("due", day["date"]),
                    "needs": item.get("needs", []), "state": s,
                })
    by_key = {t["key"]: t for t in tasks}
    for t in tasks:
        blockers = [n for n in t["needs"]
                    if by_key.get(f"{t['day']}::{n}", {}).get("state", {}).get("done") is not True]
        t["blockers"] = blockers
        t["out"] = is_out(t["state"], today)
        t["done"] = t["state"].get("done") is True
        t["waiting"] = not t["done"] and not t["out"] and bool(blockers)

    # TODAY, never "the newest day in days.json" — those differ whenever nothing
    # was authored for today, and this tool answers "what is due today". The
    # page does the same thing from the browser clock; the two must agree.
    today_day = today
    board = [t for t in tasks if on_board(t, today_day)]
    for t in board:
        t["rolled"] = t["day"] != today_day
    rolled = [t for t in board if t["rolled"]]
    current = [t for t in board if not t["out"]]
    ready = sorted((t for t in current if not t["done"] and not t["waiting"]),
                   key=lambda t: (t["p"], not t.get("rolled", False)))
    return {
        "today": today_day, "current": current, "rolled": rolled,
        "moved": [t for t in tasks if t["state"].get("moved")],
        "next": ready[0] if ready else None,
        "done_n": sum(1 for t in current if t["done"]), "total_n": len(current),
    }


def due_label(t: dict, today: str) -> str:
    if t["done"]:
        at = t["state"].get("done_at", "")
        return f"{C['dim']}done {at[11:16]}{C['off']}" if at else f"{C['dim']}done{C['off']}"
    if t["waiting"]:
        return f"{C['yel']}waiting on {len(t['blockers'])}{C['off']}"
    # A returned push is due on the day it came back to, not on the day it was
    # authored for — same rule as dueBadge() in static/todo.js.
    s = t["state"]
    due = s["until"] if s.get("moved") == "pushed" and s.get("until") else t["due"]
    if due < today:
        n = (date.fromisoformat(today) - date.fromisoformat(due)).days
        return f"{C['red']}{n} day{'s' if n > 1 else ''} overdue{C['off']}"
    if due == today:
        return f"{C['yel']}due today{C['off']}"
    return f"{C['dim']}due {due}{C['off']}"


def show(doc: dict, state: dict, today: str, store: str) -> None:
    v = build_view(doc, state, today)
    # Same trim daily.py applies, so the terminal and the board header cannot
    # read differently for the same date ("Sat 05 Sep" vs "Sat 5 Sep").
    pretty = date.fromisoformat(v["today"]).strftime("%a %d %b %Y").replace(" 0", " ")
    print(f"\n{C['bold']}{pretty}{C['off']} · {v['done_n']}/{v['total_n']} done · {C['dim']}{store}{C['off']}")
    if v["next"]:
        print(f"\n{C['bold']}DO NEXT{C['off']}  {C['red']}P{v['next']['p']}{C['off']}  {v['next']['text']}")
    elif v["total_n"]:
        print(f"\n{C['grn']}Everything on today's list is ticked.{C['off']}")

    last = None
    for t in v["current"]:
        group = "ROLLED OVER" if t.get("rolled") else t["group"]
        if group != last:
            print(f"\n{C['dim']}{group.upper()}{C['off']}")
            last = group
        mark = "✓" if t["done"] else "☐"
        from_day = f" {C['dim']}from {t['day']}{C['off']}" if t.get("rolled") else ""
        print(f"  {mark} P{t['p']}  {t['id']:<16} {due_label(t, today)}{from_day}")

    if v["moved"]:
        revive = revivable_map(doc)
        back = sum(1 for t in v["moved"] if can_come_back(t["state"].get("reasons"), revive))
        counts = {k: sum(1 for t in v["moved"] if t["state"]["moved"] == k)
                  for k in ("parked", "pushed", "dropped")}
        summary = " · ".join(f"{k} {n}" for k, n in counts.items() if n)
        print(f"\n{C['dim']}BACKLOG{C['off']}  {summary}   "
              f"{C['grn']}{back} can come back{C['off']}   {C['dim']}./todo backlog{C['off']}")
    print()


def show_backlog(doc: dict, state: dict, today: str) -> None:
    v = build_view(doc, state, today)
    revive = revivable_map(doc)
    labels = {r["key"]: r["label"] for r in doc.get("reasons", [])}
    if not v["moved"]:
        print("\nNothing has been moved out.\n")
        return
    print(f"\n{C['bold']}Backlog{C['off']}")
    for t in sorted(v["moved"], key=lambda t: t["state"]["moved"]):
        s = t["state"]
        back = can_come_back(s.get("reasons"), revive)
        tag = f"{C['grn']}can come back{C['off']}" if back else f"{C['dim']}closed for good{C['off']}"
        until = f" until {s['until']}" if s.get("until") else ""
        print(f"\n  {C['bold']}{t['id']}{C['off']}  {s['moved']}{until}  {tag}")
        print(f"    {C['dim']}{t['text'][:78]}{C['off']}")
        for r in s.get("reasons", []):
            mark = "↩" if revive.get(r, True) else "✕"
            print(f"    {mark} {labels.get(r, r)}")
        if s.get("note"):
            print(f"    {C['dim']}note: {s['note']}{C['off']}")
        if back:
            print(f"    {C['dim']}./todo restore {t['id']}{C['off']}")
    print()


def resolve(doc: dict, name: str) -> str:
    """A bare task id resolves to today's copy, else the most recent day."""
    if "::" in name:
        return name
    hits = [f"{d['date']}::{i['id']}"
            for d in doc["days"] for g in d["groups"] for i in g["items"] if i["id"] == name]
    if not hits:
        every = sorted({i["id"] for d in doc["days"] for g in d["groups"] for i in g["items"]})
        raise SystemExit(f"[daily] no task {name!r}. Known: {', '.join(every)}")
    return hits[0]                      # days are sorted newest first


def ask_reasons(doc: dict, action: str, task_text: str) -> tuple[list, str]:
    reasons = doc.get("reasons", [])
    print(f"\n{C['bold']}{action.capitalize()}{C['off']} — {task_text}\n")
    for n, r in enumerate(reasons, 1):
        tag = f"{C['grn']}can come back{C['off']}" if r.get("revivable") else f"{C['dim']}closed for good{C['off']}"
        print(f"  {n}  {r['label']:<48} {tag}")
    while True:
        raw = input(f"\nReasons (numbers, comma-separated): ").strip()
        try:
            picked = [reasons[int(x) - 1]["key"] for x in raw.replace(" ", "").split(",") if x]
        except (ValueError, IndexError):
            print(f"  {C['red']}Enter numbers from the list, e.g. 1,3{C['off']}")
            continue
        if picked:
            return picked, input("Note (optional, Enter to skip): ").strip()
        print(f"  {C['red']}Pick at least one reason.{C['off']}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="daily", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="show",
                    choices=["show", "done", "undone", "park", "push", "drop",
                             "restore", "backlog", "history"])
    ap.add_argument("task", nargs="?")
    ap.add_argument("--reason", action="append", default=[],
                    help="reason key; repeatable. Skips the interactive prompt")
    ap.add_argument("--note", default=None)
    ap.add_argument("--until", default=None, help="return date for push (YYYY-MM-DD)")
    ap.add_argument("-n", type=int, default=20, help="history length")
    args = ap.parse_args()

    doc = load_doc()
    today = date.today().isoformat()
    try:
        state = db.get_state()["tasks"]
        store = "postgresql"
    except Exception as exc:                                    # noqa: BLE001
        raise SystemExit(f"[daily] database unreachable: {exc}\n"
                         f"[daily] is PostgreSQL running? the page falls back to "
                         f"localStorage, but this tool has nothing to fall back to.")

    if args.command == "show":
        return show(doc, state, today, store)
    if args.command == "backlog":
        return show_backlog(doc, state, today)
    if args.command == "history":
        labels = {r["key"]: r["label"] for r in doc.get("reasons", [])}
        for e in db.history(args.n):
            rs = " + ".join(labels.get(r, r) for r in (e.get("reasons") or []))
            print(f"  {e['at'][:16]}  {e['action']:<9} {e['key']:<34} {rs}"
                  + (f"  — {e['note']}" if e.get("note") else ""))
        return

    if not args.task:
        raise SystemExit(f"[daily] {args.command} needs a task id. Try: ./todo")
    key = resolve(doc, args.task)
    action = {"park": "parked", "push": "pushed", "drop": "dropped",
              "done": "done", "undone": "undone", "restore": "restored"}[args.command]
    op = {"key": key, "action": action}

    if action == "restored":
        # `backlog` already withholds the `./todo restore` hint from a task whose
        # reasons are all terminal — so this tool believed the rule and then let
        # `restore` ignore it, and the page's Restore button did the same. One
        # terminal reason closes a task; the way back is to say what changed, by
        # recording a new move with a reason that CAN come back.
        s = state.get(key, {})
        blocking = blocking_reasons(s.get("reasons"), revivable_map(doc))
        if s.get("moved") and blocking:
            labels = {r["key"]: r["label"] for r in doc.get("reasons", [])}
            revivable = [r["key"] for r in doc.get("reasons", []) if r.get("revivable")]
            raise SystemExit(
                f"[daily] {key} is closed for good by "
                + " + ".join(labels.get(r, r) for r in blocking)
                + f".\n[daily] to bring it back, say what changed — move it out again with a "
                  f"reason that can come back, then restore it:\n"
                  f"[daily]   ./todo park {args.task} --reason "
                + "|".join(revivable))

    if action in ("parked", "pushed", "dropped"):
        text = next((plain(i["task"]) for d in doc["days"] for g in d["groups"]
                     for i in g["items"] if f"{d['date']}::{i['id']}" == key), key)
        if args.reason:
            op["reasons"], op["note"] = args.reason, args.note
        elif TTY:
            op["reasons"], note = ask_reasons(doc, args.command, text)
            op["note"] = args.note or note or None
        else:
            raise SystemExit(
                f"[daily] {args.command} needs at least one --reason, and there is no "
                f"terminal to ask on.\n[daily] reasons: "
                + ", ".join(r["key"] for r in doc.get("reasons", []))
                + "\n[daily] refusing to move a task out without saying why.")
        if action == "pushed":
            op["until"] = args.until or (date.today() + timedelta(days=1)).isoformat()

    try:
        db.apply_ops([op])
    except db.OpError as exc:
        raise SystemExit(f"[daily] {exc}")
    revive = revivable_map(doc)
    extra = ""
    if op.get("reasons"):
        extra = (f" · {len(op['reasons'])} reason{'s' if len(op['reasons']) > 1 else ''}"
                 f" · {'can come back' if can_come_back(op['reasons'], revive) else 'closed for good'}")
    print(f"{C['grn']}✓{C['off']} {action} {key}{extra}")


if __name__ == "__main__":
    main()
