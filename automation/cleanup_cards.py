"""Delete the bot's temporary upGrad resume cards.

The export bot (upgrad_apply.py) clones `june_master_resume` into a per-run card
named `<slug>_ats_resume`. Those temp clones pile up. This tidies them: it logs
in (auto), opens "My Resumes", and deletes EVERY card whose name ends in
`_ats_resume`. It NEVER deletes `june_master_resume` or any card without that
suffix (i.e. your real/master resumes are left untouched). The exported PDFs
already live in each workspace, so deleting the cards loses nothing.

Cards are KEPT after export now: a card is deleted only once the application for
that job has actually been SUBMITTED, so use `--slug` for the normal case.

    automation/.venv/bin/python automation/cleanup_cards.py --slug <slug>  # delete ONE (normal)
    automation/.venv/bin/python automation/cleanup_cards.py --dry-run      # list only
    automation/.venv/bin/python automation/cleanup_cards.py                # delete ALL temp cards
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser import headed_context
import upgrad_apply as ua

SUFFIX = "_ats_resume"
PROTECTED = {"june_master_resume", "august_master_resume", "master_ic_architect",
             "august_ic_master_resume"}


def main() -> None:
    dry = "--dry-run" in sys.argv
    only = None
    if "--slug" in sys.argv:
        slug = sys.argv[sys.argv.index("--slug") + 1]
        only = f"{slug.replace('-', '_')}{SUFFIX}"
    with headed_context() as ctx:
        page = ctx.new_page()
        ua.stage_login(page)   # auto-login + land on resume-builder
        ua.stage_nav(page)     # navigate to the "My Resumes" grid
        frame = ua.app(page)

        labels = frame.locator('[aria-label^="delete "]')
        names = []
        for i in range(labels.count()):
            lbl = labels.nth(i).get_attribute("aria-label") or ""
            if lbl.startswith("delete "):
                names.append(lbl[len("delete "):])

        targets = [n for n in names if n.endswith(SUFFIX) and n not in PROTECTED]
        if only is not None:
            targets = [n for n in targets if n == only]
            if not targets:
                print(f"[cleanup] no card named {only!r} -- nothing to do", file=sys.stderr)
        print(f"[cleanup] all cards ({len(names)}): {names}", file=sys.stderr)
        print(f"[cleanup] temp cards to delete ({len(targets)}): {targets}", file=sys.stderr)
        if dry:
            print("[cleanup] --dry-run: nothing deleted", file=sys.stderr)
            return

        deleted = []
        for name in targets:
            if name in PROTECTED or not name.endswith(SUFFIX):
                continue  # belt-and-suspenders safety
            btn = frame.locator(f'[aria-label="delete {name}"]').first
            if btn.count() == 0:
                print(f"[cleanup] skip {name!r} -- delete control not found", file=sys.stderr)
                continue
            btn.click(timeout=5_000)
            confirmed = False
            for label in ("Delete", "Yes", "Confirm", "OK"):
                cand = frame.locator(
                    f'[role="dialog"] button:has-text("{label}"), '
                    f'button.ui.primary.button:has-text("{label}")'
                ).first
                if cand.count() > 0:
                    cand.click(timeout=5_000)
                    confirmed = True
                    break
            page.wait_for_timeout(2_000)
            deleted.append(name)
            print(f"[cleanup] deleted {name!r}{'' if confirmed else ' (no confirm modal seen)'}", file=sys.stderr)

        print(f"[cleanup] DONE -- deleted {len(deleted)}: {deleted}", file=sys.stderr)


if __name__ == "__main__":
    main()
