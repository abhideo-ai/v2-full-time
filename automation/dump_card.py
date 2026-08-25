#!/usr/bin/env python3
"""Dump a live Hiration card to disk. READ-ONLY -- it never writes to the card.

Why this exists: a previous session read the live card in the browser, wrote a
one-line summary into CLAUDE.md and cleared its context without saving the text.
The bullets were never on disk, so nothing in git could recover them. This script
makes that failure impossible to repeat -- run it and the card's own words land in
the repo.

It reuses upgrad_apply's login/nav/open stages verbatim, then only READS:
  - #PR_designation_N / #PR_company_N   (contenteditable divs, stable ids)
  - #PR-child-N .public-DraftEditor-content   (the Draft.js bullet editor)
Both innerText and innerHTML are captured, because <strong> is the thing that
does not survive a hand-drag copy and is exactly what we care about preserving.

    automation/.venv/bin/python automation/dump_card.py [--card NAME] [--max-index 20]

Run from the repo root -- the persistent browser profile lives there.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import upgrad_apply as ua  # noqa: E402
from browser import headed_context  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CARD = "august_ic_master_resume"


def read_text(frame, sel: str) -> str:
    return frame.evaluate(
        "(s) => { const el = document.querySelector(s); "
        "return el ? (el.innerText || '').trim() : ''; }", sel)


def read_html(frame, sel: str) -> str:
    return frame.evaluate(
        "(s) => { const el = document.querySelector(s); "
        "return el ? el.innerHTML : ''; }", sel)


def read_bullets(frame, idx: int) -> list[dict]:
    """One entry per rendered line in the Draft.js editor, text + html."""
    return frame.evaluate(
        """(i) => {
            const root = document.querySelector('#PR-child-' + i +
                ' .public-DraftEditor-content');
            if (!root) return [];
            const blocks = root.querySelectorAll('[data-block="true"]');
            const out = [];
            blocks.forEach(b => {
                const text = (b.innerText || '').trim();
                if (text) out.push({text, html: b.innerHTML});
            });
            return out;
        }""", idx)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default=DEFAULT_CARD)
    ap.add_argument("--max-index", type=int, default=20,
                    help="highest PR-child-N index to probe")
    ap.add_argument("--out", default="master/live_card_dump",
                    help="output path stem (.json and .md are written)")
    args = ap.parse_args()

    with headed_context() as ctx:
        page = ctx.new_page()
        ua.stage_login(page)
        ua.stage_nav(page)
        ua.stage_find_master(page, args.card)
        ua.stage_open_copy(page, args.card)
        ua._dismiss_modals(page)
        page.wait_for_timeout(2500)
        ua._suppress_chatgpt_buttons(page)

        frame = ua.app_frame(page)
        if frame is None:
            raise SystemExit("[dump] editor iframe not attached")

        headline = read_text(frame, ua.HEADLINE_FIELD)
        roles = []
        for idx in range(args.max_index + 1):
            title = read_text(frame, f"#PR_designation_{idx}")
            company = read_text(frame, f"#PR_company_{idx}")
            bullets = read_bullets(frame, idx)
            if not (title or company or bullets):
                continue
            roles.append({
                "index": idx,
                "title": title,
                "company": company,
                "bullet_count": len(bullets),
                "bullets": bullets,
            })
            print(f"[dump] PR-child-{idx}: {title!r} @ {company!r} "
                  f"-- {len(bullets)} bullets", file=sys.stderr)

    payload = {"card": args.card, "headline": headline, "roles": roles}

    stem = ROOT / args.out
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [f"# Live Hiration card dump -- `{args.card}`", "",
             "**READ-ONLY capture. Nothing was written to the card.**", "",
             f"Headline: {headline}", ""]
    for r in roles:
        lines.append(f"## PR-child-{r['index']} -- {r['title']} @ {r['company']} "
                     f"({r['bullet_count']} bullets)")
        lines.append("")
        for n, b in enumerate(r["bullets"], 1):
            lines.append(f"{n}. {b['text']}")
        lines.append("")
    stem.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")

    total = sum(r["bullet_count"] for r in roles)
    print(f"[dump] {len(roles)} roles, {total} bullets -> "
          f"{stem.with_suffix('.json').relative_to(ROOT)} + "
          f"{stem.with_suffix('.md').relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
