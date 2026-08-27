#!/usr/bin/env python3
"""Write side of `jobs_tracker_v2` — seat registration and score refresh.

    automation/.venv/bin/python automation/jobs_sync.py             # seed + scores + bullets
    automation/.venv/bin/python automation/jobs_sync.py --scores    # scores only
    automation/.venv/bin/python automation/jobs_sync.py --bullets   # bullets only
    automation/.venv/bin/python automation/jobs_sync.py --scores --bullets
    automation/.venv/bin/python automation/jobs_sync.py --dry-run

⚠ It writes wherever `jobs_db.DSN` points, which is `jobs_tracker_v2` — v2's own
database since 2026-08-26. v1's ninety-two rows are in `jobs_tracker` and are not
reachable from here at all.

Deliberately NOT in `jobs_db.py`: the server imports that one, and the thing the
server imports must not be able to mutate the record.

All three passes are idempotent — re-run them as often as you like:

  seed     inserts the v2 seats that exist only as directories. ON CONFLICT DO
           NOTHING, so a re-run never overwrites a status he has changed since.

  scores   re-reads every workspace's `score.json` and refreshes `fit_score` /
           `fit_breakdown` from its `weighted_total`. Scores get re-adjudicated —
           three of the four moved on 2026-08-25 alone — so tonight's numbers are
           never hardcoded anywhere; this reads them back off disk.

  bullets  re-reads every `upgrad_resume.html`, master included, and rebuilds
           `resume_bullets` from it. Same shape as `scores`, and the same
           direction: THE FILE IS THE SOURCE, the table is an index over it.
           Editing a row changes nothing about what the exporter writes and is
           gone at the next sync. A wrong bullet is fixed in the résumé.

`scores` only ever touches a row whose slug has a workspace WITH a score.json in
this repo, and refuses any row still carrying a v1 five-axis breakdown.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jobs_db  # noqa: E402
import upgrad_resume_paste as urp  # noqa: E402

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
    INSERT INTO applications (slug, type, company, role, source_url, source_note, location, status)
    VALUES (%(slug)s, 'full_time', %(company)s, %(role)s, %(source_url)s, %(source_note)s,
            %(location)s, %(status)s::application_status)
    ON CONFLICT (slug) DO NOTHING
    RETURNING id
"""


def register(slug: str, company: str, role: str, *, status: str = "resume_drafted",
             source_url: str | None = None, location: str | None = None,
             source_note: str | None = None) -> bool:
    """Put one seat on the launcher. True if it was new. Never overwrites."""
    row = {
        "slug": slug, "company": company, "role": role, "status": status,
        "location": location,
        # A URL or NULL. Never prose: the launcher reads this column as an href,
        # so "(no URL supplied)" rendered as a broken link that looked real.
        # Migration 007 made the column nullable precisely so this can be None.
        "source_url": source_url if (source_url or "").startswith(("http://", "https://")) else None,
        "source_note": source_note,
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


# ---------------------------------------------------------------------------
# bullets — the derived `resume_bullets` index
# ---------------------------------------------------------------------------
# ⛔ ONE DIRECTION ONLY:
#
#     upgrad_resume.html  ->  resume_bullets  ->  rendered pages / PDF / .docx
#
# Nothing here ever writes a résumé file, and nothing downstream may either. The
# exporter reads `upgrad_resume.html`; a bullet authored in Postgres and copied
# back out is exactly the drift that merging three résumé files into one removed
# on 2026-08-25. See db/migrations/010_resume_bullets.sql.

# Hygiene, per CLAUDE.md's per-bullet rules. Computed once at sync so a query can
# ask "which bullets break the rules" without re-deriving anything.
_VERB_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_BOLD_RE = re.compile(r"<(?:strong|b)\b", re.I)


def leading_verb(text: str) -> str | None:
    """The bullet's first word, punctuation stripped. None if it has none.

    CLAUDE.md: "Leading verb unique across the résumé — same-root variants
    collide". This is the word that rule is about; the stem check against the
    rest of the file is a query, not a column.
    """
    m = _VERB_RE.search(text)
    return m.group(0) if m else None


def hygiene(text: str, html: str, kind: str) -> dict:
    return {
        # Off the experience sections there is no "leading verb" — the skills
        # block is capability labels, not sentences — so NULL, not a wrong word.
        "leading_verb": leading_verb(text) if kind == "experience" else None,
        # ⛔ NOT len(text.split()). CLAUDE.md's measurement traps name that
        # counter by name: it counts a standalone " — " as a word, so a 25-word
        # bullet reports as 26 and "four bullets were trimmed that did not need
        # trimming". Count only tokens containing [A-Za-z0-9] — the same rule
        # `hygiene_check.py:words()` and SQL's `resume_word_count()` use.
        # Corrected 2026-08-27; it disagreed with both on 34 of the master's 91
        # bullets and reported 3 false over-25s. Re-run `--bullets` to refresh.
        "word_count":   sum(1 for w in re.split(r"\s+", text) if re.search(r"[A-Za-z0-9]", w)),
        "has_bold":     bool(_BOLD_RE.search(html)),
        # Mechanical proxy. "Scale marker or measurable outcome" is judgement.
        "has_number":   bool(re.search(r"[0-9%]", text)),
    }


def resume_sources() -> dict[str, Path]:
    """{source -> résumé path} for every résumé in the repo, master included.

    `master` is a source like any other and is what a seat's bullets are compared
    AGAINST — "which bullets are unique to this seat, and which came from the
    master" is the question that needs it in the same table.
    """
    found = {}
    master = ROOT / "master" / "upgrad_resume.html"
    if master.exists():
        found["master"] = master
    for slug, rel in jobs_db.workspace_paths().items():
        path = ROOT / rel / "upgrad_resume.html"
        if path.exists():
            found[slug] = path
    return found


def bullet_rows(source: str, path: Path) -> tuple[list[dict], list[str]]:
    """(rows, missing section ids) for one résumé. Pure — touches no database."""
    parsed = urp.parse_sections(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rel = path.relative_to(ROOT).as_posix()
    rows = []
    for sec in parsed["sections"]:
        role = sec["role"] or {}
        for i, block in enumerate(sec["blocks"], 1):
            rows.append({
                "source": source, "source_path": rel, "source_sha256": digest,
                "section_id": sec["id"], "section_kind": sec["kind"],
                "section_label": sec["label"], "card_only": sec["card_only"],
                "company": role.get("company"), "role_title": role.get("role_title"),
                "date_from": role.get("date_from"), "date_to": role.get("date_to"),
                "location": role.get("location"),
                "ord": i, "text": block["text"], "html": block["html"],
                **hygiene(block["text"], block["html"], sec["kind"]),
            })
    return rows, parsed["missing"]


_BULLET_INSERT = """
    INSERT INTO resume_bullets (
        application_id, source, source_path, source_sha256,
        section_id, section_kind, section_label, card_only,
        company, role_title, date_from, date_to, location,
        ord, text, html, leading_verb, word_count, has_bold, has_number)
    VALUES (
        %(application_id)s, %(source)s, %(source_path)s, %(source_sha256)s,
        %(section_id)s, %(section_kind)s, %(section_label)s, %(card_only)s,
        %(company)s, %(role_title)s, %(date_from)s, %(date_to)s, %(location)s,
        %(ord)s, %(text)s, %(html)s, %(leading_verb)s, %(word_count)s,
        %(has_bold)s, %(has_number)s)
"""


def sync_bullets(dry_run: bool = False, only: list[str] | None = None) -> dict:
    """Rebuild `resume_bullets` from the résumé files. Returns a summary.

    Every file is parsed BEFORE anything is written, and the writes are one
    transaction: a résumé being rewritten by another agent mid-run cannot leave
    half a résumé in the table. A source that parses to nothing is reported and
    SKIPPED — its existing rows are left alone, because wiping good rows over a
    file caught mid-write is the worse failure.

    `only` limits the run to named sources; the default is every résumé there is.
    """
    sources = resume_sources()
    if only:
        sources = {k: v for k, v in sources.items() if k in only}

    parsed, skipped, missing = {}, [], {}
    for source, path in sorted(sources.items()):
        try:
            rows, gaps = bullet_rows(source, path)
        except Exception as exc:                                     # noqa: BLE001
            skipped.append((source, f"unparseable: {exc}"))
            continue
        if not rows:
            skipped.append((source, "parsed to zero bullets — left as it stands"))
            continue
        parsed[source] = rows
        if gaps:
            missing[source] = gaps

    summary = {"sources": len(parsed), "bullets": sum(len(r) for r in parsed.values()),
               "missing": missing, "skipped": skipped, "unregistered": []}
    if dry_run:
        for source, rows in sorted(parsed.items()):
            print(f"[bullets] would refresh {source}: {len(rows)} bullet(s)")
    else:
        with jobs_db.connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT slug, id FROM applications")
            ids = {r["slug"]: r["id"] for r in cur.fetchall()}
            for source, rows in sorted(parsed.items()):
                app_id = ids.get(source)          # None for 'master', and for a
                if source != "master" and app_id is None:   # workspace not yet
                    summary["unregistered"].append(source)  # registered.
                cur.execute("DELETE FROM resume_bullets WHERE source = %s", (source,))
                for row in rows:
                    cur.execute(_BULLET_INSERT, {**row, "application_id": app_id})
                print(f"[bullets] {source}: {len(rows)} bullet(s)"
                      f" across {len({r['section_id'] for r in rows})} section(s)")
            conn.commit()

    for source, gaps in sorted(missing.items()):
        print(f"[bullets] {source}: section(s) NOT FOUND — {', '.join(gaps)}"
              " (a misspelt id is skipped silently by the exporter too)", file=sys.stderr)
    for source, why in skipped:
        print(f"[bullets] {source}: {why}", file=sys.stderr)
    for source in summary["unregistered"]:
        print(f"[bullets] {source}: workspace on disk but no row in applications —"
              " bullets stored with a NULL application_id", file=sys.stderr)
    print(f"[bullets] {summary['sources']} source(s), {summary['bullets']} bullet(s)"
          + (f", {len(skipped)} skipped" if skipped else ""))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scores", action="store_true", help="refresh scores, skip the seed")
    ap.add_argument("--bullets", action="store_true",
                    help="rebuild resume_bullets from the résumé files, skip the seed")
    ap.add_argument("--dry-run", action="store_true", help="say what would change, change nothing")
    args = ap.parse_args()
    # A bare run does all three. Naming any pass runs exactly the passes named,
    # so --scores --bullets is both and neither implies the seed.
    picked = args.scores or args.bullets
    if not picked:
        seed(args.dry_run)
    if args.scores or not picked:
        sync_scores(args.dry_run)
    if args.bullets or not picked:
        sync_bullets(args.dry_run)
    print(json.dumps(jobs_db.launcher()["counts"], indent=2))


if __name__ == "__main__":
    main()
