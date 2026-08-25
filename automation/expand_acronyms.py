#!/usr/bin/env python3
"""Expand acronyms on first use in the interview-prep pages.

    automation/.venv/bin/python automation/expand_acronyms.py [--dry-run]

The rulebook requires every acronym expanded on first use, in reading order,
everywhere — not just in résumé bullets. These pages are read under interview
pressure, so nothing on them should need decoding.

Only PROSE is touched. Mermaid blocks, <code>, <pre>, <script>, <style> and tag
attributes are masked out first: expanding an acronym inside a diagram would
rename a node and break the render, which is a worse defect than the one being
fixed.

Idempotent — an acronym already followed by "(ACRONYM)" or already expanded
earlier on the page is left alone.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP = ROOT / "killer-query-case-studies" / "prep"

# Ordered: longer/more specific first so P95 is not eaten by a P9 rule.
EXPANSIONS = [
    ("P99", "99th-percentile (P99)"),
    ("P95", "95th-percentile (P95)"),
    ("P50", "50th-percentile (P50)"),
    ("P0", "priority-zero (P0)"),
    ("SQL", "structured query language (SQL)"),
    ("JSON", "JavaScript Object Notation (JSON)"),
    ("SLA", "service-level agreement (SLA)"),
    ("API", "application programming interface (API)"),
    ("VPC", "virtual private cloud (VPC)"),
    ("UI", "user interface (UI)"),
    ("AI", "artificial intelligence (AI)"),
]

# Regions whose contents must never be edited.
MASK = re.compile(
    r"(<pre\b[^>]*>.*?</pre>"
    r"|<code\b[^>]*>.*?</code>"
    r"|<script\b[^>]*>.*?</script>"
    r"|<style\b[^>]*>.*?</style>"
    r"|<[^>]+>)",                      # any tag, so attributes are safe too
    re.S | re.I,
)


def expand(html: str) -> tuple[str, list[str]]:
    parts = MASK.split(html)
    done: list[str] = []
    # Even indices are prose, odd indices are masked regions.
    for acro, full in EXPANSIONS:
        if acro in done:
            continue
        # Already expanded anywhere in prose? then nothing to do.
        prose = "".join(parts[i] for i in range(0, len(parts), 2))
        if f"({acro})" in prose:
            continue
        pat = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(acro)}(?![A-Za-z0-9])")
        for i in range(0, len(parts), 2):
            m = pat.search(parts[i])
            if not m:
                continue
            parts[i] = parts[i][: m.start()] + full + parts[i][m.end():]
            done.append(acro)
            break
    return "".join(parts), done


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    pages = sorted(PREP.glob("*.html"))
    if not pages:
        raise SystemExit(f"[acronyms] no pages in {PREP}")
    total = 0
    for page in pages:
        src = page.read_text(encoding="utf-8")
        out, done = expand(src)
        if not done:
            print(f"[acronyms] {page.name:38s} nothing to expand")
            continue
        if not args.dry_run:
            page.write_text(out, encoding="utf-8")
        print(f"[acronyms] {page.name:38s} {', '.join(done)}")
        total += len(done)
    print(f"[acronyms] {total} first-use expansions"
          + (" (dry run, nothing written)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
