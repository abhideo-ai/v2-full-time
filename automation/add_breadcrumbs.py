#!/usr/bin/env python3
"""Inject a breadcrumb into the killer-query case-study pages.

    automation/.venv/bin/python automation/add_breadcrumbs.py

These pages are imported content: each is a self-contained HTML file with its
own <style> block and its own design tokens, so the breadcrumb is injected in
their language rather than linked to the workspace stylesheet.

IDEMPOTENT by design — it skips any page that already carries a breadcrumb, so
it is safe to re-run whenever new pages (the prep set) land.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CS = ROOT / "killer-query-case-studies"

NAMES = {
    "kq1-precedent-search": "Precedent search",
    "kq2-outcome-correlation": "Outcome correlation",
    "kq3-override-intelligence": "Override intelligence",
    "kq4-early-signal-detection": "Early-signal detection",
    "kq5-decision-latency": "Decision latency",
    "kq6-ai-vs-human": "AI versus clinician",
    "kq7-confidence-calibration": "Confidence calibration",
    "kq8-policy-friction": "Policy friction",
    "kq9-causal-path": "Causal path",
    "kq10-cross-domain": "Cross-domain analytics",
}

CSS = """
/* breadcrumb — injected by automation/add_breadcrumbs.py */
.crumb{font-family:var(--mono,ui-monospace,Menlo,monospace);font-size:.72rem;letter-spacing:.06em;
 color:var(--steel,#51626D);margin:0 0 26px;display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.crumb a{color:var(--teal-deep,#084F4B);text-decoration:none;border-bottom:1px solid transparent}
.crumb a:hover{border-bottom-color:var(--teal,#0B756F)}
.crumb .sep{color:var(--hairline,#D5DFE1)}
.crumb .here{color:var(--ink,#12222C);font-weight:500}
"""


def trail(path: Path) -> list[tuple[str, str | None]]:
    """(label, href) pairs. href None means 'you are here'."""
    rel = path.relative_to(CS)
    up = "../" * len(rel.parents[:-1])          # depth below killer-query-case-studies/
    root = f"{up}../index.html"
    csindex = f"{up}index.html"

    if rel.as_posix() == "index.html":
        return [("Full-time JD workspace", root), ("Case studies", None)]
    if rel.as_posix() == "summary.html":
        return [("Full-time JD workspace", root), ("Case studies", csindex), ("Summary", None)]

    stem = rel.stem
    if rel.parent.name == "prep":
        name = NAMES.get(stem, stem)
        return [("Full-time JD workspace", root), ("Case studies", csindex),
                ("Interview prep", None), (name, None)]
    if stem.endswith("-qa"):
        base = stem[:-3]
        name = NAMES.get(base, base)
        return [("Full-time JD workspace", root), ("Case studies", csindex),
                (name, f"{up}{base}.html"), ("Q&A", None)]
    name = NAMES.get(stem, stem)
    return [("Full-time JD workspace", root), ("Case studies", csindex), (name, None)]


def render(pairs) -> str:
    bits = []
    for i, (label, href) in enumerate(pairs):
        if i:
            bits.append('<span class="sep">›</span>')
        bits.append(f'<a href="{href}">{label}</a>' if href
                    else f'<span class="here">{label}</span>')
    return '<p class="crumb">' + "".join(bits) + "</p>"


def main() -> None:
    pages = sorted(CS.rglob("*.html"))
    if not pages:
        raise SystemExit(f"[crumbs] no pages under {CS}")
    done = skipped = 0
    for page in pages:
        s = page.read_text(encoding="utf-8")
        if 'class="crumb"' in s:
            skipped += 1
            continue
        if "</style>" not in s or "<main" not in s:
            print(f"[crumbs] SKIP {page.relative_to(ROOT)} — no <style> or no <main>", file=sys.stderr)
            skipped += 1
            continue
        s = s.replace("</style>", CSS + "</style>", 1)
        s = re.sub(r"(<main[^>]*>)", r"\1\n" + render(trail(page)), s, count=1)
        page.write_text(s, encoding="utf-8")
        print(f"[crumbs] {page.relative_to(ROOT)}")
        done += 1
    print(f"[crumbs] {done} injected, {skipped} already had one or were unsuitable")


if __name__ == "__main__":
    main()
