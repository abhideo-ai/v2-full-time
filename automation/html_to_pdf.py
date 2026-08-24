"""Render local HTML file(s) to PDF via headless Chromium (Playwright).

Faithful to the page's CSS — bold, colors, and layout survive (unlike a
browser "Print to PDF" that can flatten formatting). Applies @media print.

Usage (from repo root):
    automation/.venv/bin/python automation/html_to_pdf.py <file.html> [<file2.html> ...]

Each <name>.html is written to a sibling <name>.pdf.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def main(paths):
    if not paths:
        raise SystemExit("usage: html_to_pdf.py <file.html> [...]")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        for raw in paths:
            html = Path(raw).resolve()
            if not html.is_file():
                print(f"SKIP (missing) {raw}", file=sys.stderr)
                continue
            out = html.with_suffix(".pdf")
            page.goto(html.as_uri(), wait_until="load")
            page.emulate_media(media="print")
            opts = dict(
                path=str(out),
                format="A4",
                print_background=True,
                margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"},
            )
            # Accessibility: tagged PDF (structure tags for screen readers) +
            # outline (bookmarks from headings). Supported on Playwright >= 1.42;
            # fall back cleanly on older versions.
            try:
                page.pdf(tagged=True, outline=True, **opts)
                tag = "tagged+outline"
            except TypeError:
                page.pdf(**opts)
                tag = "untagged (Playwright too old for tagged PDF)"
            print(f"OK {out}  [{tag}]")
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
