#!/usr/bin/env python3
"""Render ONLY the narration sections of professional-journey.md.

    professional-journey-narration.html  <- what he reads before and during a call

Pulls five sections verbatim from the markdown: the three career-narration
lengths, and the two role narrations that carry an architect interview.
Deliberately does NOT touch professional-journey.html, which is generated
separately by journey_to_html.py.

    python3 automation/journey_narration_html.py
"""
import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "professional-journey.md"
OUT = ROOT / "professional-journey-narration.html"

WANTED = [
    ("SHORT", "career"),
    ("MEDIUM", "career"),
    ("LONG", "career"),
    ("Role narration — Deque Software", "role"),
    ("Role narration — VoltusWave, second stint", "role"),
]


def section(md_text, prefix):
    """Grab '## <prefix>...' through to the next '## ' heading."""
    m = re.search(r"^## (%s[^\n]*)$" % re.escape(prefix), md_text, flags=re.M)
    if not m:
        return None, None
    start = m.end()
    nxt = re.search(r"^## ", md_text[start:], flags=re.M)
    body = md_text[start:start + nxt.start()] if nxt else md_text[start:]
    return m.group(1).strip(), body.strip()


def main():
    if not SRC.exists():
        sys.exit("missing %s" % SRC)
    raw = SRC.read_text(encoding="utf-8")

    chunks, toc, missing = [], [], []
    for prefix, kind in WANTED:
        title, body = section(raw, prefix)
        if body is None:
            missing.append(prefix)
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        md = markdown.Markdown(extensions=["tables", "sane_lists", "attr_list"])
        rendered = md.convert(body)
        # The blockquotes ARE the spoken lines — mark them so they stand out.
        rendered = re.sub(r"<blockquote>", '<blockquote class="pj-say">', rendered)
        # Titles carry inline markdown (**bold**) — render it rather than escaping it.
        head = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(title))
        chunks.append(
            '<section class="pj-narr pj-narr-%s" id="%s">\n<h2>%s</h2>\n%s\n</section>'
            % (kind, slug, head, rendered)
        )
        toc.append('<li><a href="#%s">%s</a></li>' % (slug, head))

    if missing:
        print("!! missing sections: %s" % ", ".join(missing))

    page = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Narration — what to say</title>
  <link rel="icon" type="image/svg+xml" href="./static/favicon.svg" />
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<nav class="toolbar no-print" aria-label="Primary">
  <span class="breadcrumb" aria-label="Breadcrumb">
    <a href="./index.html">Full-time v2</a>
    <span class="sep">/</span>
    <a href="./professional-journey.html">Professional journey</a>
    <span class="sep">/</span>
    <strong aria-current="page">Narration</strong>
  </span>
  <span class="spacer"></span>
  <a class="button" href="./professional-journey.html">Full speaking view</a>
  <a class="button" href="./professional-journey.md">Full record + research</a>
</nav>

<main class="page narrow" id="main">
  <header>
    <h1>Narration</h1>
    <p class="pj-lede">The lines themselves. <strong>Indented blocks are what you say out loud</strong> &mdash;
    everything else is a note about how to say it. Pick the length by how much room you have, not by how much
    you want to cover.</p>
    <p class="pj-stats">
      <span class="pj-stat"><strong>~40s</strong> short</span>
      <span class="pj-stat pj-stat-default"><strong>~90s</strong> medium &middot; default</span>
      <span class="pj-stat"><strong>~3m</strong> long</span>
      <span class="pj-stat"><strong>2</strong> role stories</span>
    </p>
  </header>

  <nav class="pj-toc no-print" aria-label="Sections"><ol>
%(toc)s
  </ol></nav>

%(body)s

</main>
</body>
</html>
""" % {"toc": "\n".join(toc), "body": "\n\n".join(chunks)}

    OUT.write_text(page, encoding="utf-8")
    print("wrote %s (%d bytes) — %d sections" % (OUT.name, len(page), len(chunks)))


if __name__ == "__main__":
    main()
