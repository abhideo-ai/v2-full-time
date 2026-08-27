#!/usr/bin/env python3
"""Open a headed Chromium against upGrad so you can log in once.

The browser uses a persistent profile (.playwright-profile/) so the cookies
you save here are reused by automation/upgrad_apply.py on subsequent runs.

upGrad polls the URL for the /login suffix going away — auto-exits once you've
signed in (5-min timeout). Works when launched from a background runner that
has no interactive stdin.

Usage:
    automation/.venv/bin/python automation/login.py        # opens upgrad
    automation/.venv/bin/python automation/login.py upgrad
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser import headed_context

SITES = {
    "upgrad": "https://careers.upgrad.com",
}

UPGRAD_TIMEOUT_S = 5 * 60


def _wait_for_upgrad_login(page) -> None:
    """Auto-login with stored creds if available; else poll until '/login' is gone."""
    from upgrad_creds import auto_login, get_creds

    if get_creds() is not None:
        print("Stored creds found -- attempting automatic upGrad login...")
        if auto_login(page):
            print(f"Signed in -- now at {page.url}. Session saved.")
            return
        print("Auto-login failed -- falling back to manual sign-in.")
    print("Sign in in the browser window. Polling URL for 5 min...")
    start = time.time()
    while time.time() - start < UPGRAD_TIMEOUT_S:
        page.wait_for_timeout(1500)
        if "/login" not in page.url.lower():
            page.wait_for_timeout(2500)  # let cookies flush to disk
            print(f"Signed in -- now at {page.url}. Session saved.")
            return
    print("Did not detect signed-in state within 5 min.")
    print("If you did sign in, cookies are still persisted in .playwright-profile/.")


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "upgrad"
    url = SITES.get(target)
    if not url:
        sys.exit(f"unknown site: {target}. choose one of: {', '.join(SITES)}")

    with headed_context() as ctx:
        page = ctx.new_page()
        page.goto(url)

        if target == "upgrad":
            _wait_for_upgrad_login(page)
            return

        print(f"Opened {url}. Sign in, then press Enter here to close.")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    # ⛔ RETIRED 2026-08-27 — see automation/upgrad_retired.py
    from upgrad_retired import refuse
    refuse("login.py (headed upGrad login)")
    main()
