#!/usr/bin/env python3
"""Read-only view of the `jobs_tracker_v2` database, for the workspace launcher.

    JOBS_TRACKER_DSN=dbname=jobs_tracker_v2   (default)

⚠ `jobs_tracker_v2`, not `jobs_tracker`. v2 has its own database as of
2026-08-26 (`db/migrations/004`, `005`, `006`) so that v1's ninety-two rows are
not merely filtered out of every view but are in a database nothing here opens.
His words: "let's use a different database? like jobs_tracker_v2? this way we DO
NOT interfere with v1 jobs?" The env var still overrides, but pointing it at
`jobs_tracker` would hand this module v1's record — and `tab_for` would raise on
the first archived row rather than render it.

The launcher used to carry its application cards as hand-written markup, so the
page showed four rows while the database held ninety-two. "The database is the
search layer; directories are storage, not an index" — so the page reads from
here instead, and `automation/serve.py` exposes it at `GET /api/jobs`.

Nothing in this module writes. Seeding a new seat and refreshing its score are
`automation/jobs_sync.py`'s job, deliberately kept in a separate file so the
thing the server imports cannot mutate the record by accident.

Sibling of `db.py` (the daily log's store), same connection pattern, different
database. The two never share a connection or a transaction.
"""
import json
import os
import re
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("JOBS_TRACKER_DSN", "dbname=jobs_tracker_v2")
ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Status -> launcher tab
# ---------------------------------------------------------------------------
# Eleven `application_status` values, six launcher tabs — v1's tab set exactly.
# He asked for v1's launcher back, and its tabs with it. Every row lands in
# exactly ONE tab and none may silently vanish: `tab_for` raises on an unknown
# status rather than dropping the row, and `counts()` asserts the tabs total the
# row count.
#
# There is deliberately NO `all` tab, exactly as in v1.
#
# ⚠ THERE IS NO `archived` TAB, AND NO ARCHIVE CONCEPT AT ALL. There was one,
# for a day: migration 003 archived v1's 92 rows in place and gave them a
# seventh tab. Migration 006 reversed it, because a row that has to be filtered
# out of every view is a row in the wrong database — v1's record lives in
# `jobs_tracker` now and v2 never opens it. `archived` is not in this map, not
# in `TABS`, and not even in `jobs_tracker_v2`'s enum, so a row carrying it is
# refused by PostgreSQL before this module can be asked for its tab.
#
# The reasoning, tab by tab:
#
#   ready — "Ready to apply"
#       recommended_apply · resume_drafted · resume_finalized
#       The apply queue: decided to pursue, and not yet sent. v1's tab was this
#       broad (its stage map put jd-saved, changes-drafted and resume-finalized
#       all in `ready`) and its count is the backlog gate CLAUDE.md is organised
#       around — "23 rows sitting in the ready tab, unsent".
#
#   applied — "Applied"
#       applied. It went out and nothing has come back yet.
#
#   closed — "No longer available"
#       withdrawn. He pulled out, or the seat went away. Terminal, and NOT a
#       rejection: v1's record is explicit that conflating the two loses the
#       only thing the row still says.
#
#   heard-back — "Heard back"
#       heard_back · interviewing · offer. They replied and the process is live.
#       This tab set has no interviewing tab, and burying a live process in
#       `other` would be the worst answer available.
#
#   not-selected — "Not selected"
#       rejected.
#
#   other — "Other"
#       new · recommended_skip. The catch-all, which is what a catch-all is for.
#       It also retires the judgement call v2 inherited: 49 `recommended_skip`
#       rows were scored and adjudicated out before any build, and they belong
#       neither in the apply queue (they would corrupt the backlog gate) nor
#       among seats that closed on their own.
TAB_FOR_STATUS = {
    "new":               "other",
    "recommended_apply": "ready",
    "recommended_skip":  "other",
    "resume_drafted":    "ready",
    "resume_finalized":  "ready",
    "applied":           "applied",
    "heard_back":        "heard-back",
    "interviewing":      "heard-back",
    "offer":             "heard-back",
    "rejected":          "not-selected",
    "withdrawn":         "closed",
}

# The tabs in index.html, in their rendered order. `ready` is the default.
TABS = ["ready", "applied", "closed", "heard-back", "not-selected", "other"]


class UnknownStatus(KeyError):
    """A status with no tab. Raised, never swallowed — a dropped row is the
    one failure mode this whole module exists to prevent."""


def tab_for(status: str) -> str:
    try:
        return TAB_FOR_STATUS[status]
    except KeyError as exc:
        raise UnknownStatus(
            f"status {status!r} has no launcher tab — add it to TAB_FOR_STATUS"
        ) from exc


# ---------------------------------------------------------------------------
# The two scores
# ---------------------------------------------------------------------------
# CLAUDE.md scores a seat twice: TECHNICAL (target 95+, the one he cares about)
# and NON-TECHNICAL / functional (informational, never a gate). `applications`
# predates that split and carries one composite `fit_score`, so both numbers are
# read out of `fit_breakdown` rather than stored twice.
#
#   v2 seats  — jobs_sync.py writes {"rubric": "v2-weighted", "technical": N}
#               straight from the workspace's score.json `weighted_total`.
#               No non-technical number is computed in v2, so it renders "—".
#
#   v1 seats  — the five-axis breakdown splits cleanly along the same line, so
#               this is a rescale of v1's own axes, not a new judgement:
#                 technical      = hard_reqs               (out of 40)
#                 non-technical  = level + domain
#                                + location + freshness    (out of 55)
#               Both are rescaled to /100 so the columns are readable together.
#               They are NOT comparable to a v2 weighted total — different
#               rubrics — which is why the payload also carries `rubric`.
V1_TECH_MAX = 40                                        # hard_reqs
V1_FUNC = {"level": 20, "domain": 20, "location": 10, "freshness": 5}
V1_FUNC_MAX = sum(V1_FUNC.values())                     # 55


def _num(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def scores(breakdown: dict | None) -> dict:
    """-> {"technical": float|None, "non_technical": float|None, "rubric": str}"""
    b = breakdown or {}
    tech = _num(b.get("technical"))
    non_tech = _num(b.get("non_technical"))
    rubric = b.get("rubric")

    if tech is None and _num(b.get("hard_reqs")) is not None:
        tech = round(100 * _num(b["hard_reqs"]) / V1_TECH_MAX, 1)
        rubric = rubric or "v1-five-axis"
    if non_tech is None and all(_num(b.get(k)) is not None for k in V1_FUNC):
        non_tech = round(100 * sum(_num(b[k]) for k in V1_FUNC) / V1_FUNC_MAX, 1)
        rubric = rubric or "v1-five-axis"

    return {"technical": tech, "non_technical": non_tech, "rubric": rubric}


# ---------------------------------------------------------------------------
# Workspace on disk
# ---------------------------------------------------------------------------
# `applications` has no path column. Workspaces live at Month-YYYY/DD/<slug>/,
# with `upgrad_apply.py` also honouring a root-level <slug>/. v1's rows have no
# workspace in THIS repo, so their cards link out to the posting instead — which
# is honest: there is nothing local to open.
_MONTH_DIR = re.compile(r"^[A-Z][a-z]+-\d{4}$")


def workspace_paths() -> dict[str, str]:
    """slug -> repo-relative directory, for every workspace on disk."""
    found: dict[str, str] = {}
    for month in ROOT.iterdir():
        if not month.is_dir() or not _MONTH_DIR.match(month.name):
            continue
        for day in month.iterdir():
            if not day.is_dir() or not day.name.isdigit():
                continue
            for ws in day.iterdir():
                if ws.is_dir():
                    found[ws.name] = f"{month.name}/{day.name}/{ws.name}"
    return found


def _href(path: str | None) -> str | None:
    """Prefer the workspace's own index.html; fall back to the directory."""
    if not path:
        return None
    return f"{path}/index.html" if (ROOT / path / "index.html").exists() else f"{path}/"


# ---------------------------------------------------------------------------
# Intake-date group notes
# ---------------------------------------------------------------------------
# The launcher groups rows by the date they came in, the way v1's did. The date
# and the number of seats under it are DERIVED. The clause after them is not
# derivable from anything in the database — in v1 it was written by hand — so it
# is read from a file he can edit and is simply absent until he does. A header
# that reads "2026-08-25 — 4 seats" is correct; one that invents a narrative
# about what those seats were is the failure this workspace exists to avoid.
NOTES_FILE = Path(__file__).resolve().parent / "intake_notes.json"


def intake_notes() -> dict[str, str]:
    """{"2026-08-25": "…"} — hand-authored, never generated. {} when unset."""
    try:
        raw = json.loads(NOTES_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    notes = raw.get("notes") if isinstance(raw, dict) else None
    if not isinstance(notes, dict):
        return {}
    return {k: v for k, v in notes.items() if isinstance(k, str) and isinstance(v, str) and v}


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
def connect() -> psycopg.Connection:
    return psycopg.connect(DSN, row_factory=dict_row)


# `salary` is deliberately absent: compensation is deferred by user directive,
# so it is not selected, not returned, and not renderable on the launcher.
_SELECT = """
    SELECT id, slug, type, company, role, status, location,
           source_url, fit_score, fit_breakdown, applied_at, updated_at, scraped_at
      FROM applications
"""

# Once a seat has been sent, when it was sent is the fact that matters; before
# that it is when the row last moved.
SENT_STATUSES = {"applied", "heard_back", "interviewing", "offer", "rejected"}


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _row(r: dict, paths: dict[str, str]) -> dict:
    tab = tab_for(r["status"])
    path = paths.get(r["slug"])
    at, at_kind = (r["applied_at"], "applied") if r["status"] in SENT_STATUSES and r["applied_at"] \
        else (r["updated_at"] or r["scraped_at"], "updated")
    return {
        "id": r["id"],
        "slug": r["slug"],
        "type": r["type"],
        "company": r["company"],
        "role": r["role"],
        "status": r["status"],
        "tab": tab,
        "location": r["location"] or None,
        "source_url": r["source_url"] if str(r["source_url"]).startswith("http") else None,
        "source_note": None if str(r["source_url"]).startswith("http") else r["source_url"],
        "workspace": path,
        "href": _href(path),
        "fit_score": r["fit_score"],
        **scores(r["fit_breakdown"]),
        "at": _iso(at),
        "at_kind": at_kind,
        # The intake date, and what the launcher groups rows by.
        "intake": _iso(r["scraped_at"])[:10] if r["scraped_at"] else None,
    }


def applications() -> list[dict]:
    """Every row, newest activity first. No filtering — the page tabs on `tab`."""
    paths = workspace_paths()
    with connect() as conn, conn.cursor() as cur:
        cur.execute(_SELECT + " ORDER BY updated_at DESC NULLS LAST, id DESC")
        return [_row(r, paths) for r in cur.fetchall()]


def counts(rows: list[dict]) -> dict:
    """Per-tab counts plus the row total. Asserts the tabs account for every row
    — a launcher that quietly renders 90 of 96 rows is worse than one that fails
    loudly. There is no `all` tab, exactly as in v1; `total` carries that number
    for the page title."""
    per = {t: 0 for t in TABS}
    for r in rows:
        per[tab_for(r["status"])] += 1
    total = sum(per.values())
    if total != len(rows):
        raise AssertionError(f"tabs hold {total} rows but {len(rows)} were read")
    return {"total": len(rows), **per}


def groups(rows: list[dict]) -> list[dict]:
    """Rows bucketed by intake date, newest first — what the page renders.

    The date and the seat count are derived. `note` comes from
    `intake_notes.json` and is None until he writes one; nothing here composes a
    sentence about a group of seats it has only counted.
    """
    notes = intake_notes()
    dates = sorted({r["intake"] or "" for r in rows}, reverse=True)
    return [{"date": d or None, "note": notes.get(d)} for d in dates]


def launcher() -> dict:
    rows = applications()
    return {"store": "postgresql", "counts": counts(rows),
            "groups": groups(rows), "applications": rows}


if __name__ == "__main__":
    payload = launcher()
    print(json.dumps(payload["counts"], indent=2))
    print(f"{len(payload['applications'])} application(s)"
          f" in {len(payload['groups'])} intake group(s)")
