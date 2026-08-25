#!/usr/bin/env python3
"""Read-only view of the `jobs_tracker` database, for the workspace launcher.

    JOBS_TRACKER_DSN=dbname=jobs_tracker   (default)

The launcher used to carry its application cards as hand-written markup, so the
page showed four rows while the database held ninety-two. "The database is the
search layer; directories are storage, not an index" — so the page reads from
here instead, and `automation/serve.py` exposes it at `GET /api/jobs`.

Nothing in this module writes. Seeding a new seat and refreshing its score are
`automation/jobs_sync.py`'s job, deliberately kept in a separate file so the
thing the server imports cannot mutate v1's record by accident.

Sibling of `db.py` (the daily log's store), same connection pattern, different
database. The two never share a connection or a transaction.
"""
import os
import re
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("JOBS_TRACKER_DSN", "dbname=jobs_tracker")
ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Status -> launcher tab
# ---------------------------------------------------------------------------
# Eleven `application_status` values, nine launcher tabs. Every row lands in
# exactly ONE tab and none may silently vanish — `tab_for` raises on an unknown
# status rather than dropping the row, and `counts()` asserts the total.
#
# The reasoning, tab by tab:
#
#   new -> parked
#       Scraped, never triaged: no score, no decision, no workspace. It is not
#       `building` (nothing is being built) and not `closed` (nothing was
#       decided). `parked` is the launcher's "set aside, can come back" bucket,
#       which is exactly what an untriaged intake row is. 15 rows, 14 of them
#       v1's freelancing pipeline.
#
#   recommended_apply -> building
#       The decision to pursue is made; the workspace is the next step. It
#       belongs with the active build queue, not in a queue tab that does not
#       exist.
#
#   recommended_skip -> closed        *** the deliberate one — 49 rows ***
#       These were scored and adjudicated out before any build started, each
#       with its `rec_reasoning` on the row. Three tabs could plausibly hold
#       them and two would do real damage:
#         - `parked` would bury the handful of builds he actually paused and
#           might revive under 49 rows he already declined.
#         - `building`/`ready` would corrupt the ready-and-unsent count, which
#           is the backlog gate and the one number v2 is organised around.
#       `closed` is the archive: decided, not pursued, not coming back on its
#       own. That is what these are. They stay visible and countable there.
#
#   resume_drafted    -> building     workspace under way
#   resume_finalized  -> ready        exported/finalised and unsent — the gate
#   applied           -> sent
#   heard_back        -> responded
#   interviewing      -> interviewing
#
#   offer -> interviewing
#       There is no offer tab. An offer is the furthest-along LIVE process, so
#       it sits with the other live one rather than in `responded`, which reads
#       as "they replied". Zero rows today; revisit if a tab is ever added.
#
#   rejected  -> not-selected
#   withdrawn -> closed
#       He pulled out. Terminal, and not a rejection — v1's record is explicit
#       that conflating the two loses the only thing the row still says.
TAB_FOR_STATUS = {
    "new":               "parked",
    "recommended_apply": "building",
    "recommended_skip":  "closed",
    "resume_drafted":    "building",
    "resume_finalized":  "ready",
    "applied":           "sent",
    "heard_back":        "responded",
    "interviewing":      "interviewing",
    "offer":             "interviewing",
    "rejected":          "not-selected",
    "withdrawn":         "closed",
}

# The pills in index.html, in their rendered order. `all` is virtual.
TABS = ["building", "ready", "sent", "responded", "interviewing",
        "parked", "closed", "not-selected"]


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
# Queries
# ---------------------------------------------------------------------------
def connect() -> psycopg.Connection:
    return psycopg.connect(DSN, row_factory=dict_row)


# `salary` is deliberately absent: compensation is deferred by user directive,
# so it is not selected, not returned, and not renderable on the launcher.
_SELECT = """
    SELECT id, slug, type, company, role, status, location, source_url,
           fit_score, fit_breakdown, applied_at, updated_at, scraped_at
      FROM applications
"""

# Once a seat has been sent, when it was sent is the fact that matters; before
# that it is when the row last moved.
_APPLIED_TABS = {"sent", "responded", "interviewing", "not-selected"}


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _row(r: dict, paths: dict[str, str]) -> dict:
    tab = tab_for(r["status"])
    path = paths.get(r["slug"])
    at, at_kind = (r["applied_at"], "applied") if tab in _APPLIED_TABS and r["applied_at"] \
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
        "workspace": path,
        "href": _href(path),
        "fit_score": r["fit_score"],
        **scores(r["fit_breakdown"]),
        "at": _iso(at),
        "at_kind": at_kind,
    }


def applications() -> list[dict]:
    """Every row, newest activity first. No filtering — the page tabs on `tab`."""
    paths = workspace_paths()
    with connect() as conn, conn.cursor() as cur:
        cur.execute(_SELECT + " ORDER BY updated_at DESC NULLS LAST, id DESC")
        return [_row(r, paths) for r in cur.fetchall()]


def counts(rows: list[dict]) -> dict:
    """Per-tab counts. Asserts the tabs account for every row — a launcher that
    quietly renders 90 of 96 rows is worse than one that fails loudly."""
    per = {t: 0 for t in TABS}
    for r in rows:
        per[r["tab"]] += 1
    total = sum(per.values())
    if total != len(rows):
        raise AssertionError(f"tabs hold {total} rows but {len(rows)} were read")
    return {"all": len(rows), **per}


def launcher() -> dict:
    rows = applications()
    return {"store": "postgresql", "counts": counts(rows), "applications": rows}


if __name__ == "__main__":
    import json
    payload = launcher()
    print(json.dumps(payload["counts"], indent=2))
    print(f"{len(payload['applications'])} application(s)")
