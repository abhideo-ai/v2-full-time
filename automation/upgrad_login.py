#!/usr/bin/env python3
"""Open a headed browser on the upGrad resume builder and wait for you to sign in.

    automation/.venv/bin/python automation/upgrad_login.py

Run from the repo root -- the persistent profile lives at ./.playwright-profile
and cwd decides which one is used.

WHY THIS EXISTS
---------------
stage_login authenticates careers.upgrad.com from the encrypted credentials and
that part works: it reaches /courses every time. But the resume builder is
Hiration embedded in an iframe (careers.upgrad.com/upgrad-hiration.html), and
that has its OWN session established through an upGrad -> Hiration handshake.
When that session dies, the iframe renders "Login Failed / If you're using
incognito mode, please check if cookies are enabled" and never recovers -- it
sat in that state for 26 seconds in testing, so it is not a timing problem.

Nothing scripted re-establishes it. It takes one real sign-in, after which the
persistent profile carries the session again and the headless runs work.

Separately, and already fixed in browser.py: third-party cookies must be
allowed or the iframe never mounts at all. Both problems produce the same
"Login Failed" text, which is why they were easy to confuse -- see CHROMIUM_ARGS.

This script writes nothing and touches no card. It opens the page, waits for the
resume grid to appear, and reports what it sees so you know the session took.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import upgrad_apply as ua  # noqa: E402
from browser import headed_context  # noqa: E402

WAIT_MINUTES = 10


def main() -> None:
    os.environ.pop("UPGRAD_HEADLESS", None)  # always headed; the point is to interact
    print("Opening upGrad. Sign in if prompted -- this window is yours.", file=sys.stderr)
    print(f"Waiting up to {WAIT_MINUTES} min for the resume grid to appear.\n", file=sys.stderr)

    with headed_context(headless=False) as ctx:
        page = ctx.new_page()

        # Watch the endpoint that mints the Hiration session. On 2026-08-27 it
        # answered 400 "Null or empty token cannot be authenticated", with no
        # Authorization and no Cookie header on the request, while a valid
        # upgrad-auth-token.production cookie sat in the profile. Capturing it
        # during a REAL sign-in shows whether a manual login sends a token the
        # scripted one does not -- which is the whole open question.
        def on_resp(resp):
            if "resume/builder/auth" not in resp.url:
                return
            hdrs = {k.lower() for k in resp.request.headers}
            try:
                body = resp.text()[:200]
            except Exception:                                    # noqa: BLE001
                body = "<unreadable>"
            print(f"  [auth-api] {resp.status} "
                  f"auth-header={'authorization' in hdrs} "
                  f"cookie-header={'cookie' in hdrs} :: {body}", file=sys.stderr)

        page.on("response", on_resp)
        page.goto("https://careers.upgrad.com/resume-builder",
                  wait_until="domcontentloaded", timeout=60_000)

        deadline = WAIT_MINUTES * 60 * 1000
        waited = 0
        step = 3000
        while waited < deadline:
            page.wait_for_timeout(step)
            waited += step
            try:
                frame = ua.app(page)
                if frame.locator('text="My Resumes"').count() > 0:
                    print("\n[ok] Signed in -- 'My Resumes' is visible.", file=sys.stderr)
                    names = frame.locator('[aria-label^="edit "]').count()
                    print(f"[ok] {names} resume card(s) visible in the grid.", file=sys.stderr)
                    print("[ok] Session saved to ./.playwright-profile -- "
                          "headless runs should work now.", file=sys.stderr)
                    page.wait_for_timeout(2000)
                    return
                body = " ".join(frame.locator("body").inner_text(timeout=3000).split())
                if "Login Failed" in body:
                    status = "iframe still says 'Login Failed' -- sign in, or sign out and back in"
                else:
                    status = (body[:70] or "(iframe empty)")
            except Exception:
                status = "(iframe not ready)"
            print(f"  {waited // 1000:3d}s  {status}", file=sys.stderr)

        print("\n[timeout] Never reached the resume grid. Leaving the browser state as-is.",
              file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
