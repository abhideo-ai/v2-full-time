#!/usr/bin/env python3
"""Correct the card-only material on the IC master Hiration card.

    automation/.venv/bin/python automation/fix_master_card.py [--dry-run]

The exporter overwrites the TEN parsed sections on every run, so those never
need fixing by hand. Everything else on the card — the five pre-2016 roles,
their titles, companies and dates — is card-only: the bot never touches it, and
it was inherited from the v1 leadership card.

The one that matters is EL PASO. The card calls it "Senior .NET Developer" and
describes rewriting a Java application INTO .NET. The journey document says the
opposite: it was a Senior Java Developer role — JSP and Java Enterprise Edition,
Tennessee Gas Pipeline. Left alone it hides four of the eleven Java years, on a
résumé whose headline now leads with Java.

Title and company are contenteditable divs with stable ids (PR_designation_N,
PR_company_N); the bullets are a Draft.js editor inside #PR-child-N, so they go
through the same _paste_html path the exporter uses and keep their formatting.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import upgrad_apply as ua  # noqa: E402
from browser import headed_context  # noqa: E402

CARD = "august_ic_master_resume"

# index -> (expected current title, new title, new bullets or None to leave)
FIXES = {
    8: {
        "expect": "Senior .NET Developer",
        "title": "Senior Java Developer",
        "company": "El Paso Corporation",
        "bullets": [
            "Translated a Citrix-hosted <strong>Java</strong> application onto "
            "<strong>JSP and Java Enterprise Edition</strong> for Tennessee Gas Pipeline, an "
            "<strong>11,800-mile</strong> interstate system",
            "Shipped the Nominations, Flowing Gas and Contracts modules covering the federal "
            "scheduling workflow for interstate gas transport across <strong>4 years</strong>",
            "Refactored the data layer through a <strong>SQL Server 2000 to 2005</strong> "
            "upgrade, with stored-procedure rewrites and index design across the scheduling "
            "modules",
        ],
    },
}


def read_field(frame, sel: str) -> str:
    return frame.evaluate(
        "(s) => { const el = document.querySelector(s); "
        "return el ? (el.innerText || '').trim() : '<missing>'; }", sel)


def set_contenteditable(frame, sel: str, text: str) -> None:
    """Set a contenteditable div and fire the events React listens for.

    Assigning innerText alone leaves React's state untouched and the change is
    discarded on the next render, so the input event has to be dispatched too.
    """
    frame.evaluate(
        """([s, t]) => {
            const el = document.querySelector(s);
            if (!el) throw new Error("no element for " + s);
            el.focus();
            const range = document.createRange();
            range.selectNodeContents(el);
            const sel = window.getSelection();
            sel.removeAllRanges(); sel.addRange(range);
            document.execCommand("insertText", false, t);
            el.dispatchEvent(new Event("input", {bubbles: true}));
            el.dispatchEvent(new Event("change", {bubbles: true}));
            el.blur();
        }""",
        [sel, text],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change, write nothing")
    args = ap.parse_args()

    with headed_context() as ctx:
        page = ctx.new_page()
        ua.stage_login(page)
        ua.stage_nav(page)
        ua.stage_find_master(page, CARD)
        ua.stage_open_copy(page, CARD)
        ua._dismiss_modals(page)
        page.wait_for_timeout(2000)
        ua._suppress_chatgpt_buttons(page)

        frame = ua.app_frame(page)
        if frame is None:
            raise SystemExit("[fix] editor iframe not attached")

        changed = 0
        for idx, fix in FIXES.items():
            d_sel, c_sel = f"#PR_designation_{idx}", f"#PR_company_{idx}"
            cur_title, cur_co = read_field(frame, d_sel), read_field(frame, c_sel)
            print(f"[fix] PR-child-{idx}: {cur_title!r} @ {cur_co!r}", file=sys.stderr)

            title_ok = cur_title == fix["title"]
            if title_ok:
                print(f"[fix]   title already {fix['title']!r}", file=sys.stderr)
            elif cur_title != fix["expect"]:
                print(f"[fix]   *** expected {fix['expect']!r}, found {cur_title!r} — "
                      f"NOT touching it ***", file=sys.stderr)
                continue
            if args.dry_run:
                print(f"[fix]   would set title and rewrite {len(fix['bullets'])} bullets",
                      file=sys.stderr)
                continue

            if not title_ok:
                set_contenteditable(frame, d_sel, fix["title"])
                page.wait_for_timeout(700)
                print(f"[fix]   title now {read_field(frame, d_sel)!r}", file=sys.stderr)

            # Bullets are rewritten whether or not the title already matched —
            # a corrected title over stale .NET bullets is the worst of both.
            before = read_field(frame, f"#PR-child-{idx} {ua.BODY}")[:60]
            ua.replace_bullets(page, f"#PR-child-{idx} {ua.BODY}", fix["bullets"])
            page.wait_for_timeout(1200)
            ua._wait_for_save(page, None)
            after = read_field(frame, f"#PR-child-{idx} {ua.BODY}")[:60]
            print(f"[fix]   bullets before: {before!r}", file=sys.stderr)
            print(f"[fix]   bullets after : {after!r}", file=sys.stderr)
            changed += 1

        if changed and not args.dry_run:
            ua._wait_for_save(page, None)
            page.wait_for_timeout(2500)
            print(f"[fix] OK -- {changed} role(s) corrected on {CARD}", file=sys.stderr)
        elif not changed:
            print("[fix] nothing to change", file=sys.stderr)
        ua.shot(page, "fix-master-card")


if __name__ == "__main__":
    main()
