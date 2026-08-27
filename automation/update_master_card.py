#!/usr/bin/env python3
"""Write the merged VoltusWave and Deque blocks INTO the IC master card, then export it.

    automation/.venv/bin/python automation/update_master_card.py --dry-run
    automation/.venv/bin/python automation/update_master_card.py

Why this exists, and how it differs from upgrad_apply.py
--------------------------------------------------------
`upgrad_apply.py --slug master` CLONES `august_ic_master_resume` into
`master_ats_resume`, overwrites the ten parsed sections in the CLONE from
master/upgrad_resume.html, and exports the clone. The master card itself is
never written -- it is in cleanup_cards.py's PROTECTED set and is only ever
read.

That is right for a per-seat résumé and wrong when the master card itself has
drifted from the master file. On 2026-08-27 the card carried 10 VoltusWave and
14 Deque bullets while the file carried 10 and 6; the merge takes the file to
24 and 12. Leaving the card behind means every future clone starts from stale
content, and the card-only material around it (education, certifications, the
five pre-2016 roles) is inherited by every export.

So this script opens the master card DIRECTLY -- no clone -- writes the two
merged blocks, and exports that card. It is the same primitive fix_master_card.py
uses for the pre-2016 roles: stage_find_master + stage_open_copy on CARD, then
replace_bullets through _paste_html, which is the only path that carries both
bold and bullet glyphs into Draft.js.

⚠ THIS WRITES TO A PROTECTED CARD. The restore point is the committed read-only
capture at master/live_card_dump.json. Take a fresh one with
`automation/dump_card.py --card august_ic_master_resume` before running if the
card may have changed since.

Source of truth is master/upgrad_resume.html -- this script parses it rather
than carrying its own copy, so the file and the card cannot drift apart here.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import upgrad_apply as ua  # noqa: E402
from browser import headed_context  # noqa: E402

CARD = "august_ic_master_resume"
REPO = Path(__file__).resolve().parent.parent
MASTER_HTML = REPO / "master" / "upgrad_resume.html"
PDF_OUT = REPO / "master" / "Abhisheik_Deo_Resume.pdf"

# PR-child index -> (section id in master/upgrad_resume.html, expected company).
# Order verified 2026-08-27 against master/live_card_dump.json: entry 0 is the
# VoltusWave second stint, entry 1 is Deque. The expected-company guard is the
# same safety fix_master_card.py uses -- it refuses rather than silently
# rewriting the wrong role if the card's entry order ever changes.
TARGETS = {
    0: ("quick-vp", "Voltuswave"),
    1: ("quick-deque", "Deque"),
}


def section_bullets(html: str, section_id: str) -> list[str]:
    """Inner HTML of each <p> in one section of the master résumé."""
    i = html.find(f'id="{section_id}"')
    if i < 0:
        raise SystemExit(f"no section id={section_id!r} in {MASTER_HTML}")
    after = [x for x in (html.find('id="quick-', i + 10),
                         html.find('id="p-', i + 10)) if x > 0]
    seg = html[i:min(after)] if after else html[i:]
    out = [b.strip() for b in re.findall(r"<p>(.*?)</p>", seg, re.S)]
    if not out:
        raise SystemExit(f"section {section_id!r} parsed to zero bullets -- refusing")
    return out


def read_field(frame, sel: str) -> str:
    return frame.evaluate(
        "(s) => { const el = document.querySelector(s); "
        "return el ? (el.innerText || '').trim() : '<missing>'; }", sel)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report what is on the card and what would replace it; write nothing")
    ap.add_argument("--no-export", action="store_true",
                    help="write the card but skip the PDF export")
    args = ap.parse_args()

    html = MASTER_HTML.read_text(encoding="utf-8")
    plan = {idx: (sid, company, section_bullets(html, sid))
            for idx, (sid, company) in TARGETS.items()}
    for idx, (sid, _company, bullets) in plan.items():
        print(f"[plan] PR-child-{idx} <- #{sid}: {len(bullets)} bullets", file=sys.stderr)

    with headed_context() as ctx:
        page = ctx.new_page()
        ua.stage_login(page)
        ua.stage_nav(page)
        ua.stage_find_master(page, CARD)
        ua.stage_open_copy(page, CARD)
        frame = ua.app(page)

        changed = 0
        for idx, (sid, expect_company, bullets) in plan.items():
            c_sel = f"#PR_company_{idx}"
            d_sel = f"#PR_designation_{idx}"
            cur_co = read_field(frame, c_sel)
            cur_title = read_field(frame, d_sel)
            print(f"[card] PR-child-{idx}: {cur_title!r} @ {cur_co!r}", file=sys.stderr)

            if expect_company.lower() not in cur_co.lower():
                ua.fail(page, "guard",
                        f"PR-child-{idx} company is {cur_co!r}, expected to contain "
                        f"{expect_company!r} -- refusing to write the wrong role")

            before = read_field(frame, f"#PR-child-{idx} {ua.BODY}")
            n_before = len([l for l in before.splitlines() if l.strip()])
            print(f"[card] PR-child-{idx}: {n_before} bullets now -> {len(bullets)} after",
                  file=sys.stderr)

            if args.dry_run:
                continue

            ua.replace_bullets(page, f"#PR-child-{idx} {ua.BODY}", bullets)
            page.wait_for_timeout(1200)
            after = read_field(frame, f"#PR-child-{idx} {ua.BODY}")
            n_after = len([l for l in after.splitlines() if l.strip()])
            if n_after != len(bullets):
                print(f"[warn] PR-child-{idx} reads {n_after} bullets after write, "
                      f"expected {len(bullets)}", file=sys.stderr)
            changed += 1

        if args.dry_run:
            print("[dry-run] nothing written", file=sys.stderr)
            return

        ua._wait_for_save(page, None)
        print(f"[card] wrote {changed} section(s) to {CARD}", file=sys.stderr)

        if args.no_export:
            return
        pdf = ua.stage_export(page, "master", output=str(PDF_OUT))
        if pdf:
            print(f"[export] {pdf}", file=sys.stderr)
            ua.stage_verify("master", pdf)


if __name__ == "__main__":
    # ⛔ RETIRED 2026-08-27 — see automation/upgrad_retired.py
    from upgrad_retired import refuse
    refuse("update_master_card.py (writes into the Hiration card)")
    main()
