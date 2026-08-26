#!/usr/bin/env python3
"""Write side of `jobs_tracker_v2` — seat registration and score refresh.

    automation/.venv/bin/python automation/jobs_sync.py            # seed + scores
    automation/.venv/bin/python automation/jobs_sync.py --scores   # scores only
    automation/.venv/bin/python automation/jobs_sync.py --dry-run

⚠ It writes wherever `jobs_db.DSN` points, which is `jobs_tracker_v2` — v2's own
database since 2026-08-26. v1's ninety-two rows are in `jobs_tracker` and are not
reachable from here at all.

Deliberately NOT in `jobs_db.py`: the server imports that one, and the thing the
server imports must not be able to mutate the record.

Both passes are idempotent — re-run them as often as you like:

  seed    inserts the v2 seats that exist only as directories. ON CONFLICT DO
          NOTHING, so a re-run never overwrites a status he has changed since.

  scores  re-reads every workspace's `score.json` and refreshes `fit_score` /
          `fit_breakdown` from its `weighted_total`. Scores get re-adjudicated —
          three of the four moved on 2026-08-25 alone — so tonight's numbers are
          never hardcoded anywhere; this reads them back off disk.

`scores` only ever touches a row whose slug has a workspace WITH a score.json in
this repo, and refuses any row still carrying a v1 five-axis breakdown.
"""
import argparse
import json
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jobs_db  # noqa: E402

ROOT = jobs_db.ROOT

# One-time backfill: the four seats built before the launcher read the database.
# New seats are registered by `resume.py new` and never come through here.
SEEDS = [
    {
        "slug": "wipro-principal-software-architect",
        "company": "Wipro",
        "role": "Principal Software Architect",
        # Inbound LinkedIn InMail from a Wipro recruiter — no posting, no JD, no
        # location, and so no technical score. `recommended_apply` rather than
        # `new`: he is pursuing it (workspace, research, drafted reply), the
        # rubric just has nothing to weight yet.
        "status": "recommended_apply",
        "location": None,
        "source_url": "linkedin-inmail (inbound recruiter outreach — no URL supplied)",
    },
    {
        "slug": "o9-senior-architect-agentic",
        "company": "o9 Solutions (via Recruit Right)",
        "role": "Senior Architect — Software & Agentic Engineering",
        "status": "resume_drafted",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "source_url": "naukri (listing URL not captured)",
    },
    {
        "slug": "principal-architect-ai-native",
        "company": "Foreign MNC (via Axihire)",
        "role": "Principal / Chief Architect — AI-Native & Agentic Systems",
        "status": "resume_drafted",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "source_url": "naukri (blind posting, client undisclosed — listing URL not captured)",
    },
    {
        "slug": "yes-madam-lead-architect",
        "company": "Yes Madam",
        "role": "Lead Architect",
        "status": "resume_drafted",
        "location": "Sector 63, Noida (Work From Office)",
        "source_url": "naukri (listing URL not captured)",
    },
]

_INSERT = """
    INSERT INTO applications (slug, type, company, role, source_url, location, status)
    VALUES (%(slug)s, 'full_time', %(company)s, %(role)s, %(source_url)s,
            %(location)s, %(status)s::application_status)
    ON CONFLICT (slug) DO NOTHING
    RETURNING id
"""


def register(slug: str, company: str, role: str, *, status: str = "resume_drafted",
             source_url: str | None = None, location: str | None = None) -> bool:
    """Put one seat on the launcher. True if it was new. Never overwrites."""
    row = {
        "slug": slug, "company": company, "role": role, "status": status,
        "location": location,
        # A URL or NULL. Never prose: the launcher reads this column as an href,
        # so "(no URL supplied)" rendered as a broken link that looked real.
        # Migration 007 made the column nullable precisely so this can be None.
        "source_url": source_url if (source_url or "").startswith(("http://", "https://")) else None,
    }
    with jobs_db.connect() as conn, conn.cursor() as cur:
        cur.execute(_INSERT, row)
        created = cur.fetchone() is not None
        conn.commit()
    return created


def seed(dry_run: bool = False) -> int:
    added = 0
    for s in SEEDS:
        if dry_run:
            print(f"[jobs] would seed {s['slug']} ({s['status']})")
            continue
        if register(**{k: v for k, v in s.items() if k != "status"}, status=s["status"]):
            print(f"[jobs] seeded {s['slug']} as {s['status']}")
            added += 1
        else:
            print(f"[jobs] {s['slug']} already registered — left alone")
    return added


def read_weighted_total(path: Path) -> float | None:
    """`weighted_total` out of a workspace score.json, or None if unusable.

    Tolerant on purpose: these files are rewritten by other agents mid-session,
    so a half-written or absent one must be skipped, never crash the sync.
    """
    try:
        value = json.loads(path.read_text()).get("weighted_total")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


_UPDATE = ("UPDATE applications SET fit_score = %s, fit_breakdown = %s, updated_at = now()"
           " WHERE slug = %s")


def _update_score(cur, total: float, breakdown: dict, slug: str) -> None:
    """UPDATE the row, surviving a PostgreSQL install whose plpgsql is missing.

    ⚠ Environment, not code: this machine's server is 16.15 but the
    postgresql@16 keg has been deleted, so `$libdir/plpgsql.so` is gone and the
    table's BEFORE UPDATE `set_updated_at()` trigger cannot load. Every UPDATE on
    `applications` fails with UndefinedFile until `brew install postgresql@16`
    puts the library back. (INSERTs are unaffected — the trigger is UPDATE-only,
    and `v2_daily` has no triggers at all, so the daily log never sees this.)

    The retry runs the same statement with user triggers off for that
    transaction only. `updated_at` is set explicitly above, so the row lands
    exactly as the trigger would have left it. Once the library is restored the
    first attempt succeeds and this path stops being reached.
    """
    args = (round(total), json.dumps(breakdown), slug)
    cur.execute("SAVEPOINT before_score")
    try:
        cur.execute(_UPDATE, args)
        cur.execute("RELEASE SAVEPOINT before_score")
    except psycopg.errors.UndefinedFile:
        cur.execute("ROLLBACK TO SAVEPOINT before_score")
        print("[jobs] WARNING: this PostgreSQL cannot load plpgsql, so the updated_at"
              " trigger fails. Retrying with triggers off. Fix with:"
              " brew install postgresql@16", file=sys.stderr)
        cur.execute("SET LOCAL session_replication_role = replica")
        cur.execute(_UPDATE, args)
        cur.execute("SET LOCAL session_replication_role = origin")


def sync_scores(dry_run: bool = False) -> int:
    """Refresh fit_score / fit_breakdown from every workspace score.json."""
    updated = 0
    with jobs_db.connect() as conn, conn.cursor() as cur:
        for slug, rel in sorted(jobs_db.workspace_paths().items()):
            score_file = ROOT / rel / "score.json"
            if not score_file.exists():
                continue
            total = read_weighted_total(score_file)
            if total is None:
                print(f"[jobs] {slug}: score.json has no usable weighted_total — skipped",
                      file=sys.stderr)
                continue
            cur.execute("SELECT fit_score, fit_breakdown FROM applications WHERE slug = %s", (slug,))
            row = cur.fetchone()
            if row is None:
                print(f"[jobs] {slug}: workspace on disk but no row — run the seed first",
                      file=sys.stderr)
                continue
            if (row["fit_breakdown"] or {}).get("hard_reqs") is not None:
                # v1's five-axis breakdown. Not ours to overwrite.
                print(f"[jobs] {slug}: carries a v1 breakdown — refusing to overwrite",
                      file=sys.stderr)
                continue
            breakdown = {"rubric": "v2-weighted", "technical": total,
                         "source": f"{rel}/score.json"}
            if row["fit_score"] == round(total) and row["fit_breakdown"] == breakdown:
                continue
            if dry_run:
                print(f"[jobs] would set {slug} technical = {total}")
                continue
            _update_score(cur, total, breakdown, slug)
            print(f"[jobs] {slug}: technical = {total}")
            updated += 1
        if not dry_run:
            conn.commit()
    return updated


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scores", action="store_true", help="refresh scores only, skip the seed")
    ap.add_argument("--dry-run", action="store_true", help="say what would change, change nothing")
    args = ap.parse_args()
    if not args.scores:
        seed(args.dry_run)
    sync_scores(args.dry_run)
    print(json.dumps(jobs_db.launcher()["counts"], indent=2))


if __name__ == "__main__":
    main()
