"""Headed Playwright browser with a persistent profile.

The persistent profile (./.playwright-profile) keeps cookies and login state
across runs — important for upGrad/Hiration which gates the resume builder
behind auth.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import BrowserContext, sync_playwright

PROFILE_DIR = Path(os.environ.get("PLAYWRIGHT_PROFILE", ".playwright-profile")).resolve()

# ⚠ THIRD-PARTY COOKIES MUST BE ALLOWED, or the resume builder never loads.
#
# careers.upgrad.com/resume-builder embeds Hiration in an iframe
# (careers.upgrad.com/upgrad-hiration.html), and the page probes for third-party
# cookie support first -- it loads mindmup.github.io/3rdpartycookiecheck. When the
# probe fails the page renders "Login Failed / If you're using incognito mode,
# please check if cookies are enabled" and DOES NOT MOUNT THE IFRAME AT ALL, so
# every downstream stage fails looking for a frame that was never created.
#
# Diagnosed 2026-08-27. The failure looks like three things it is not:
#   - not a credentials problem: stage_login succeeds and reaches /courses
#   - not headless detection: headed fails identically, and headless works once
#     these flags are set
#   - not a Chromium upgrade: the bundled build (151.0.7922.34) was installed
#     24 Aug, before the exports that worked on 26 Aug
# With the flags the probe reaches 3rdpartycookiecheck/complete.html and the
# ResumeBuilder iframe appears.
CHROMIUM_ARGS = [
    "--disable-features=TrackingProtection3pcd,ThirdPartyStoragePartitioning,PrivacySandboxSettings4",
]


@contextmanager
def headed_context(slow_mo_ms: int = 0, headless: bool | None = None):
    # Default headed. Set UPGRAD_HEADLESS=1 (or pass headless=True) to run hidden.
    # Headless is viable now that login is automated (no manual sign-in) -- but
    # upGrad/Hiration may fingerprint-detect headless Chromium, so headed stays the
    # safe fallback if a headless run gets blocked or captcha'd.
    if headless is None:
        headless = os.environ.get("UPGRAD_HEADLESS", "").strip().lower() in ("1", "true", "yes", "on")
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context: BrowserContext = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            slow_mo=slow_mo_ms,
            args=CHROMIUM_ARGS,
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        try:
            yield context
        finally:
            context.close()
