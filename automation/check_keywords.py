#!/usr/bin/env python3
"""Keyword check: does another résumé document keep every technical term the master carries?

    automation/.venv/bin/python automation/check_keywords.py variant:story-clusters
    automation/.venv/bin/python automation/check_keywords.py seat:<slug>

Why: an applicant tracking system (ATS) matches words. A rewrite that leads with the
problem pushes technology names later in a bullet, and rewording can drop them without
anyone noticing. This lists every term in the master that looks technical (a name with a
capital letter or a digit inside it, an acronym, or a known multi-word product) and fails
on any term the other document no longer contains anywhere: headline, summary, skills
or bullets. Read-only.
"""
import html
import re
import sys

import psycopg

DSN = "dbname=jobs_tracker_v2"
# Capitalised words that are ordinary English, not technology.
PLAIN = {"A", "An", "The", "And", "Or", "Of", "On", "In", "For", "To", "With", "By", "At", "As",
         "From", "Into", "Over", "Under", "Every", "Each", "One", "No", "Not"}


def document_text(cur, doc_key: str) -> tuple[str, list[str]]:
    cur.execute("SELECT section_kind, html FROM resume_blocks WHERE doc_key = %s AND retired_at IS NULL",
                (doc_key,))
    rows = cur.fetchall()
    if not rows:
        sys.exit(f"check_keywords: no document {doc_key!r}")
    plain = [html.unescape(re.sub(r"<[^>]+>", " ", h)) for _, h in rows]
    return " ".join(plain), plain


def terms(texts: list[str]) -> set[str]:
    found = set()
    for t in texts:
        words = t.split()
        for i, w in enumerate(words):
            w = w.strip(",;:()[]\"'—–")
            if not w or w in PLAIN or (i == 0 and w[:1].isupper() and w[1:].islower()):
                continue                       # a bullet's leading verb, capitalised by position
            if re.search(r"[A-Z].*[A-Z]|[A-Za-z]\d|\d[A-Za-z]|^[A-Z][a-z]+[A-Z]|\.[A-Za-z]", w) or \
               (w[:1].isupper() and len(w) > 1):
                found.add(w)
    return found


def main() -> int:
    other = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        _, master_texts = document_text(cur, "master")
        other_full, _ = document_text(cur, other)
    wanted = terms(master_texts)
    # A plain Title-case word ("Retrieval") also counts when it survives in lower case;
    # acronyms and mixed-case names ("P99", "DynamoDB") must match exactly.
    def kept(t: str) -> bool:
        flags = re.I if t[:1].isupper() and t[1:].islower() else 0
        return re.search(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", other_full, flags) is not None
    missing = sorted(t for t in wanted if not kept(t))
    print(f"{len(wanted)} terms in the master; {len(wanted) - len(missing)} kept in {other}")
    for t in missing:
        print(f"  MISSING  {t}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
