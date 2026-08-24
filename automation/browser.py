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
