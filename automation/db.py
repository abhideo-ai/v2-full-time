#!/usr/bin/env python3
"""PostgreSQL state store for the daily log.

    V2_DAILY_DSN=dbname=v2_daily   (default)

The page sends OPERATIONS, not a state blob. Each op is appended to task_event
verbatim and then folded into task_state, so the current view and the history
can never disagree — there is one write path, not two.

    {"ops": [
      {"key": "2026-08-25::clone-card", "action": "done"},
      {"key": "2026-08-25::paste-jds",  "action": "parked",
       "reasons": ["posting-closed", "comp-below"],
       "note": "recruiter confirmed the band caps below floor and the req is closed"},
      {"key": "2026-08-25::source-ic",  "action": "pushed", "until": "2026-08-27"},
      {"key": "2026-08-25::source-ic",  "action": "restored"}
    ]}
"""
import os
from datetime import date

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("V2_DAILY_DSN", "dbname=v2_daily")

ACTIONS = {"done", "undone", "parked", "pushed", "dropped", "restored"}
MOVES = {"parked", "pushed", "dropped"}


class OpError(ValueError):
    """A malformed operation from the page. Surfaced as a 400, never a 500."""


def connect() -> psycopg.Connection:
    return psycopg.connect(DSN, row_factory=dict_row)


def split_key(key: str) -> tuple[date, str]:
    if not isinstance(key, str) or "::" not in key:
        raise OpError(f"key {key!r} must look like '<YYYY-MM-DD>::<task id>'")
    day_s, task_id = key.split("::", 1)
    try:
        day = date.fromisoformat(day_s)
    except ValueError as exc:
        raise OpError(f"key {key!r}: {exc}") from exc
    if not task_id:
        raise OpError(f"key {key!r} has an empty task id")
    return day, task_id


def validate(op: dict) -> tuple[date, str, str]:
    if not isinstance(op, dict):
        raise OpError("each op must be an object")
    action = op.get("action")
    if action not in ACTIONS:
        raise OpError(f"action {action!r} must be one of {sorted(ACTIONS)}")
    day, task_id = split_key(op.get("key"))
    if action in MOVES:
        reasons = op.get("reasons")
        if not isinstance(reasons, list) or not reasons:
            raise OpError(f"a '{action}' op needs a non-empty `reasons` list")
        if any(not isinstance(r, str) or not r.strip() for r in reasons):
            raise OpError(f"a '{action}' op has an empty reason in {reasons!r}")
        if len(reasons) != len(set(reasons)):
            raise OpError(f"a '{action}' op has duplicate reasons in {reasons!r}")
    if action == "pushed":
        until = op.get("until")
        if not until:
            raise OpError("a 'pushed' op needs an `until` date")
        try:
            date.fromisoformat(until)
        except (ValueError, TypeError) as exc:
            raise OpError(f"until {until!r}: {exc}") from exc
    return day, task_id, action


# Every action's effect on task_state, as a single UPSERT tail. `done` clears a
# move: ticking a parked task means you did it after all.
_SET = {
    "done":     "done = true,  done_at = now(), moved = NULL, reasons = NULL, note = NULL, until = NULL, moved_at = NULL",
    "undone":   "done = false, done_at = NULL",
    "restored": "moved = NULL, reasons = NULL, note = NULL, until = NULL, moved_at = NULL",
    "parked":   "moved = 'parked',  reasons = %(reasons)s, note = %(note)s, until = NULL,       moved_at = now()",
    "pushed":   "moved = 'pushed',  reasons = %(reasons)s, note = %(note)s, until = %(until)s,  moved_at = now()",
    "dropped":  "moved = 'dropped', reasons = %(reasons)s, note = %(note)s, until = NULL,       moved_at = now()",
}


def apply_ops(ops: list) -> dict:
    """Apply every op in ONE transaction: all of them land, or none do."""
    if not isinstance(ops, list) or not ops:
        raise OpError('expected {"ops": [ ... ]} with at least one op')
    if len(ops) > 500:
        raise OpError("too many ops in one request (max 500)")
    prepared = []
    for op in ops:
        day, task_id, action = validate(op)
        prepared.append({
            "key": op["key"], "day": day, "task_id": task_id, "action": action,
            "reasons": op.get("reasons"), "note": op.get("note"), "until": op.get("until"),
        })
    with connect() as conn, conn.cursor() as cur:
        for p in prepared:
            cur.execute(
                "INSERT INTO task_event (key, day, task_id, action, reasons, note, until)"
                " VALUES (%(key)s, %(day)s, %(task_id)s, %(action)s, %(reasons)s, %(note)s, %(until)s)",
                p,
            )
            cur.execute(
                "INSERT INTO task_state (key, day, task_id) VALUES (%(key)s, %(day)s, %(task_id)s)"
                " ON CONFLICT (key) DO UPDATE SET "
                + _SET[p["action"]]
                + ", updated_at = now()",
                p,
            )
            # A first-touch INSERT takes the DEFAULTs, so replay the effect onto
            # the fresh row too. Cheap, and it keeps insert and update identical.
            cur.execute(
                "UPDATE task_state SET " + _SET[p["action"]] + ", updated_at = now()"
                " WHERE key = %(key)s",
                p,
            )
        conn.commit()
    return get_state()


def get_state() -> dict:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT key, done, done_at, moved, reasons, note, until, moved_at, updated_at"
            " FROM task_state ORDER BY key"
        )
        tasks = {}
        for row in cur.fetchall():
            key = row.pop("key")
            tasks[key] = {
                k: (v.isoformat() if hasattr(v, "isoformat") else v)
                for k, v in row.items() if v is not None and v is not False
            }
            tasks[key]["done"] = bool(row["done"])
        return {"store": "postgresql", "tasks": tasks}


def history(limit: int = 100) -> list[dict]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT key, action, reasons, note, until, at FROM task_event"
            " ORDER BY at DESC, id DESC LIMIT %s",
            (limit,),
        )
        return [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
            for r in cur.fetchall()
        ]


if __name__ == "__main__":
    import json
    print(json.dumps({"state": get_state(), "history": history(10)}, indent=2))
