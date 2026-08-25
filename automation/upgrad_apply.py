#!/usr/bin/env python3
"""Drive upGrad's Resume Builder for one application workspace (slug).

upGrad's careers.upgrad.com/resume-builder is an SPA — URL doesn't change as
you navigate. Flow per app: clone the master resume, rename it
`<slug>_ats_resume`, overwrite every section from `<workspace>/upgrad_resume.html`.

Stages (each can be the stop point via --stop-after):
  login        open the builder, wait for manual sign-in on first run
  nav          click side-nav "Resume Builder" -> My Resumes grid
  find-master  locate the master resume card
  clone        click "Make A Copy" -> fill name -> submit
  open-copy    open the new copy in the editor, dump DOM
  edit         apply per-slug tailoring from upgrad_resume.html
  score        read the Resume Review aggregate score
  export       export PDF to <workspace>/Abhisheik_Deo_Resume.pdf
  verify       assert every expected fragment is present in the PDF
  summary      print a JSON result + write _upgrad_run.json (no DB)

Each stage targets one specific selector. On miss it dumps the page to
.debug/upgrad/error-<stage>.{html,png} and exits, so you can iterate live.

Usage:
    automation/.venv/bin/python automation/upgrad_apply.py --slug <slug>
    automation/.venv/bin/python automation/upgrad_apply.py --slug <slug> --stop-after clone
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser import headed_context  # noqa: E402
from upgrad_resume_paste import parse_slug, _slug_dir_candidates  # noqa: E402

ROOT_URL = "https://careers.upgrad.com"
URL = "https://careers.upgrad.com/resume-builder"
# Master card title in Hiration. Override with UPGRAD_MASTER_CARD or --master.
# Default is august_master_resume (2026-08-10) — the canonical card the user built.
# VoltusWave reads "Principal Software Architect", dates 2025-03-01 -> 2026-04-01,
# Deque 2019-12-01 -> 2025-02-01. Experience-entry order verified for the PR-child-0..4
# mapping: VoltusWave, Deque, Rocket, Co-Founder, Teletext (five pre-2016 roles follow,
# untouched by the bot). Prior default was june_master_resume.
#
# TWO-CARD DESIGN (2026-08-25, user's call -- supersedes the one-card note below).
# v2 is IC-only, so the IC card is the DEFAULT and the older card is the exception.
#   august_ic_master_resume -> DEFAULT. Cloned from august_master_resume, so it already
#                            carries all ten experience entries (five bot-written, five
#                            pre-2016 untouched), dates, education and certifications.
#                            Content source: master/upgrad_resume.html.
#                            NAME NOT YET FINALISED (2026-08-25) and the card may not exist
#                            yet -- until it does, stage_find_master fails loudly with a
#                            "check the card name / pass --master" message. That loud
#                            failure is deliberate: it beats silently exporting from the
#                            wrong card, which is what the old default did.
#   august_master_resume  -> kept deliberately, may still be used for future positions.
#                            Reach it with `--master august_master_resume`.
# VERIFIED 2026-08-18: passing `--master june_master_resume` for a leadership seat
# (Backbase) still produced "Principal Software Architect" -- that card was retitled
# in place at some point, so NO card produces the VP title any more. This is now the
# intended state, not drift: it matches LinkedIn and what recruiters source on, and a
# leadership JD asking for "Principal/Staff background" reads it fine.
# `master_ic_architect` was never created and is not needed.
#
# Superseded two-card design (2026-07-24, TITLE_PIVOT_PLAN.md), kept for context:
#   june_master_resume    -> was meant to read "VP of Technology" (it no longer does)
#   master_ic_architect   -> was meant to read "Principal Software Architect" (never built)
MASTER_TITLE = os.environ.get("UPGRAD_MASTER_CARD") or "august_ic_master_resume"
DEBUG_DIR = ROOT / ".debug" / "upgrad"
LOGIN_POLL_TIMEOUT_S = 5 * 60

# The upGrad Resume Builder is a Hiration SPA rendered inside an iframe.
# Everything we want to interact with (side-nav, resume cards, modals,
# editor) lives inside it -- top-level page.locator() does not see it.
APP_IFRAME = 'iframe[title="ResumeBuilder"]'


def app(page):
    """FrameLocator for the Hiration app iframe."""
    return page.frame_locator(APP_IFRAME)


def app_frame(page):
    """Frame object for the Hiration app iframe (for .content()/screenshots)."""
    el = page.query_selector(APP_IFRAME)
    return el.content_frame() if el else None

STAGES = ["login", "nav", "find-master", "clone", "open-copy", "edit", "score", "export", "verify", "summary"]

# Editor section body selectors (Hiration's Draft.js editor lives at this
# CSS path inside each *-child-0 wrapper -- verified 1 per section).
BODY = ".public-DraftEditor-content"
HEADLINE_FIELD = "#personal_title_1"

# Per-experience-entry section index in the editor (PR-child-N) is assumed
# to match the order in upgrad_resume.html (vp, deque, rocket, cofounder,
# teletext). Master template builds them in this order.


def dump(page, name: str) -> None:
    """Dump the iframe app DOM (if present) plus a screenshot."""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    html_path = DEBUG_DIR / f"{name}.html"
    outer_html_path = DEBUG_DIR / f"{name}.outer.html"
    png_path = DEBUG_DIR / f"{name}.png"
    frame = app_frame(page)
    if frame is not None:
        try:
            html_path.write_text(frame.content(), encoding="utf-8")
            outer_html_path.write_text(page.content(), encoding="utf-8")
        except Exception:
            html_path.write_text(page.content(), encoding="utf-8")
    else:
        html_path.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(png_path), full_page=True)
    print(f"  dumped {html_path.relative_to(ROOT)} + {png_path.relative_to(ROOT)}", file=sys.stderr)


def shot(page, name: str) -> None:
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    path = DEBUG_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"  screenshot {path.relative_to(ROOT)}", file=sys.stderr)


def fail(page, stage: str, msg: str) -> None:
    dump(page, f"error-{stage}")
    raise SystemExit(f"[{stage}] {msg} -- see .debug/upgrad/error-{stage}.{{html,png}}")


def prompt(msg: str) -> None:
    print(f"\n>>> {msg}", file=sys.stderr)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\naborted")


def stage_login(page) -> None:
    print(f"[login] opening {ROOT_URL}", file=sys.stderr)
    page.goto(ROOT_URL, wait_until="domcontentloaded", timeout=45_000)
    page.wait_for_timeout(2500)
    if "/login" in page.url.lower():
        from upgrad_creds import auto_login

        if not auto_login(page):
            print(
                "[login] login form -- sign in in the Chromium window (5-min poll)",
                file=sys.stderr,
            )
            start = time.time()
            while time.time() - start < LOGIN_POLL_TIMEOUT_S:
                page.wait_for_timeout(1500)
                if "/login" not in page.url.lower():
                    break
            else:
                fail(page, "login", "did not detect signed-in state within 5 min")
        page.wait_for_timeout(2000)
        print(f"[login] auth ok -- now at {page.url}", file=sys.stderr)

    print(f"[login] navigating to {URL}", file=sys.stderr)
    page.goto(URL, wait_until="domcontentloaded", timeout=45_000)
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    shot(page, "01-landing")
    print(f"[login] OK -- at {page.url}", file=sys.stderr)


def _dismiss_modals(page) -> int:
    """Clear any Ant Design modal blocking the iframe.

    upGrad shows an onboarding dialog ("Let's kickstart your career journey")
    that renders as `.ant-modal-wrap` and swallows pointer events, so every
    click inside the iframe times out with "subtree intercepts pointer events".
    It carries no close button in the markup, so Escape and mask-clicks are not
    reliable — the nodes are removed outright. Returns how many were cleared.
    """
    JS = """() => {
        const sel = ".ant-modal-wrap, .ant-modal-mask, .ant-modal-root";
        const nodes = document.querySelectorAll(sel);
        nodes.forEach(n => n.remove());
        // Ant locks scrolling while a modal is open; give it back.
        document.body.style.overflow = "";
        document.body.classList.remove("ant-scrolling-effect");
        return nodes.length;
    }"""
    cleared = 0
    # The dialog lives in the TOP-LEVEL page and overlays the iframe — clearing
    # only the app frame found nothing while every click still bounced off it.
    # Sweep every reachable frame; cross-origin ones simply throw and are skipped.
    for frame in [page.main_frame, *page.frames]:
        try:
            cleared += frame.evaluate(JS) or 0
        except Exception:                                        # noqa: BLE001
            continue
    return cleared


def stage_nav(page) -> None:
    # Wait for the iframe to mount, then act inside it.
    page.wait_for_selector(APP_IFRAME, timeout=15_000)
    cleared = _dismiss_modals(page)
    if cleared:
        print(f"[nav] dismissed {cleared} blocking modal element(s)", file=sys.stderr)
        page.wait_for_timeout(400)
    frame = app(page)
    # If "My Resumes" already visible inside the iframe, nothing to do.
    if frame.locator('text="My Resumes"').count() > 0:
        print('[nav] already at "My Resumes" inside iframe', file=sys.stderr)
        shot(page, "02-grid")
        return
    print('[nav] clicking iframe side-nav "Resume Builder"', file=sys.stderr)
    sidenav = frame.locator('text="Resume Builder"').first
    try:
        sidenav.click(timeout=10_000)
    except Exception:
        # A modal can mount after the first dismissal; clear and retry once
        # before failing, rather than losing the whole run to a dialog.
        again = _dismiss_modals(page)
        print(f"[nav] click blocked -- cleared {again} modal element(s), retrying",
              file=sys.stderr)
        page.wait_for_timeout(500)
        try:
            sidenav.click(timeout=10_000)
        except Exception as e:
            fail(page, "nav", f'could not click "Resume Builder" inside iframe: {e!r}')
    # Wait for grid heading to appear
    try:
        frame.locator('text="My Resumes"').first.wait_for(state="visible", timeout=15_000)
    except Exception as e:
        fail(page, "nav", f'"My Resumes" did not appear after click: {e!r}')
    page.wait_for_timeout(1500)
    shot(page, "02-grid")
    print("[nav] OK -- at My Resumes grid", file=sys.stderr)


def stage_find_master(page, master_title: str) -> None:
    print(f"[find-master] locating card titled {master_title!r}", file=sys.stderr)
    frame = app(page)
    title = frame.locator(f'text="{master_title}"').first
    if title.count() == 0:
        fail(
            page, "find-master",
            f"master card {master_title!r} not found -- check the card name in "
            f"Hiration, or pass --master <card> (or set UPGRAD_MASTER_CARD)",
        )
    title.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    shot(page, "03-master-card")
    print("[find-master] OK", file=sys.stderr)


def stage_clone(page, slug: str, master_title: str, reset: bool = False) -> str:
    # Existing resumes in upGrad all use underscores (e.g. master_resume_Abhisheik_Deo,
    # moniepoint_head_of_engineering). Hyphens may not validate, so normalize.
    safe_slug = slug.replace("-", "_")
    new_name = f"{safe_slug}_ats_resume"
    print(f"[clone] master -> {new_name!r}", file=sys.stderr)
    frame = app(page)

    existing = frame.locator(f'[aria-label="edit {new_name}"]').first
    if existing.count() > 0 and reset:
        print(f"[clone] --reset: deleting existing {new_name!r}", file=sys.stderr)
        del_btn = frame.locator(f'[aria-label="delete {new_name}"]').first
        if del_btn.count() == 0:
            fail(page, "clone-reset", f'no delete aria-label for {new_name!r}')
        del_btn.click(timeout=5000)
        # Confirm modal: look for a "Delete"/"Yes"/"Confirm" button
        confirm = None
        for label in ("Delete", "Yes", "Confirm", "OK"):
            cand = frame.locator(f'[role="dialog"] button:has-text("{label}"), button.ui.primary.button:has-text("{label}")').first
            if cand.count() > 0:
                confirm = cand
                break
        if confirm is not None:
            confirm.click(timeout=5000)
        page.wait_for_timeout(2500)
        existing = frame.locator(f'[aria-label="edit {new_name}"]').first  # recheck

    # Idempotency: if this resume already exists (and not reset), skip the clone and open it.
    if existing.count() > 0:
        print(f"[clone] {new_name!r} already exists -- opening it", file=sys.stderr)
        existing.click(timeout=5000)
        page.wait_for_timeout(3000)
        shot(page, "05-after-clone")
        return new_name

    copy_btn = frame.locator(f'[aria-label="copy {master_title}"]').first
    if copy_btn.count() == 0:
        fail(page, "clone", f'no aria-label "copy {master_title}"')
    copy_btn.click(timeout=5000)
    page.wait_for_timeout(1500)

    name_input = frame.locator('input[placeholder="Enter name here..."]').first
    try:
        name_input.wait_for(state="visible", timeout=10_000)
    except Exception as e:
        fail(page, "clone-modal", f"rename modal input did not appear: {e!r}")
    shot(page, "04-clone-modal")

    # React-friendly input: focus + type with small delay so onChange fires.
    name_input.click()
    name_input.press("Control+A")
    name_input.press("Delete")
    name_input.press_sequentially(new_name, delay=15)
    page.wait_for_timeout(500)

    confirm = frame.locator('button.confirmResumeName').first
    if confirm.count() == 0:
        fail(page, "clone-submit", 'no button.confirmResumeName visible')
    confirm.click(timeout=5000)
    # Wait for the modal input to actually disappear -- proves submission worked.
    try:
        name_input.wait_for(state="hidden", timeout=15_000)
    except Exception as e:
        fail(page, "clone-submit", f"modal did not close after Confirm: {e!r}")
    page.wait_for_timeout(2000)
    shot(page, "05-after-clone")
    print(f"[clone] OK -- created {new_name!r}", file=sys.stderr)
    return new_name


def stage_open_copy(page, new_name: str) -> None:
    print(f"[open-copy] opening {new_name!r}", file=sys.stderr)
    frame = app(page)
    # After clone, upGrad auto-navigates into the editor for the new resume.
    # Detect that and dump the editor; otherwise fall back to clicking Edit
    # on the card in the grid.
    if frame.locator('text="Add Section"').count() > 0:
        print("[open-copy] already in editor (auto-navigated from clone)", file=sys.stderr)
    else:
        edit_btn = frame.locator(f'[aria-label="edit {new_name}"]').first
        try:
            edit_btn.wait_for(state="visible", timeout=15_000)
        except Exception as e:
            fail(page, "open-copy-find", f'no editor + no aria-label "edit {new_name}": {e!r}')
        edit_btn.click(timeout=5000)
        page.wait_for_timeout(4000)
    dump(page, "06-editor")
    print("[open-copy] OK -- editor open, DOM dumped", file=sys.stderr)


def _suppress_chatgpt_buttons(page) -> None:
    """Hide Hiration's 'Rewrite with ChatGPT' buttons in the iframe so we
    never click them. The buttons live in <div class="chatGptComponent">."""
    frame = app_frame(page)
    if frame is None:
        return
    try:
        frame.add_style_tag(content=".chatGptComponent { display: none !important; }")
    except Exception as e:
        print(f"[edit]   could not inject suppress-css: {e!r}", file=sys.stderr)


def _focus_clear(page, selector: str) -> None:
    """Focus a Draft.js editor and DELETE ALL its content across blocks.

    Draft.js intercepts Ctrl+A in a way that only selects the current
    block. Bypass that by using the browser Selection API directly:
    range.selectNodeContents covers everything in the contenteditable
    irrespective of Draft.js's block model. Then a Backspace keystroke
    runs through Draft.js's normal beforeinput handler and deletes the
    whole selection in one shot.

    Iterates up to 6 times because a single Backspace can leave one
    'empty block' artifact in Draft.js; subsequent passes clean it up.
    """
    frame_loc = app(page)
    el = frame_loc.locator(selector).first
    el.scroll_into_view_if_needed()
    el.click()
    page.wait_for_timeout(150)
    real_frame = app_frame(page)

    def _select_all_js() -> None:
        real_frame.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) return;
                el.focus();
                const range = document.createRange();
                range.selectNodeContents(el);
                const s = window.getSelection();
                s.removeAllRanges();
                s.addRange(range);
            }""",
            selector,
        )

    def _editor_text() -> str:
        return real_frame.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                return el ? (el.innerText || "").trim() : "<missing>";
            }""",
            selector,
        )

    remaining = _editor_text()
    for _ in range(6):
        if not remaining or remaining == "<missing>":
            break
        _select_all_js()
        page.wait_for_timeout(60)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        remaining = _editor_text()

    if remaining and remaining != "<missing>":
        raise RuntimeError(
            f"could not clear {selector}: {remaining[:120]!r} still present"
        )


def _paste_html(page, html: str) -> None:
    """Dispatch a paste ClipboardEvent with text/html at the iframe's
    activeElement. Draft.js consumes HTML paste natively and preserves
    <strong>/<em>/<ul>/<li>."""
    real_frame = app_frame(page)
    if real_frame is None:
        raise RuntimeError("hiration iframe not attached")
    real_frame.evaluate(
        """(html) => {
            const ae = document.activeElement;
            if (!ae) throw new Error("no activeElement to paste into");
            const data = new DataTransfer();
            data.setData("text/html", html);
            data.setData("text/plain", new DOMParser()
                .parseFromString(html, "text/html").body.innerText);
            ae.dispatchEvent(new ClipboardEvent("paste", {
                clipboardData: data, bubbles: true, cancelable: true
            }));
        }""",
        html,
    )


def replace_singleline(page, selector: str, text: str) -> None:
    frame = app(page)
    el = frame.locator(selector).first
    el.scroll_into_view_if_needed()
    el.click()
    page.wait_for_timeout(100)
    el.press("ControlOrMeta+A")
    el.press("Delete")
    el.press_sequentially(text, delay=8)


def replace_headline_via_modal(page, text: str) -> None:
    """Clicking #personal_title_1 opens the 'Personal Information' modal
    (Hiration's edit affordance for personal fields). We use the modal's
    Job Title input + Done button rather than fighting the modal."""
    frame = app(page)
    # Open the modal by clicking the personal_title field.
    frame.locator(HEADLINE_FIELD).first.click()
    job_title = frame.locator("#socialEditorJobTitle").first
    try:
        job_title.wait_for(state="visible", timeout=10_000)
    except Exception as e:
        fail(page, "edit-headline-modal", f"Personal Info modal did not appear: {e!r}")
    job_title.fill(text)
    page.wait_for_timeout(200)
    done = frame.locator('button.ui.primary.button:has-text("Done")').first
    if done.count() == 0:
        fail(page, "edit-headline-modal", "no 'Done' button in Personal Info modal")
    done.click()
    # Wait for the modal to disappear before continuing.
    try:
        job_title.wait_for(state="hidden", timeout=10_000)
    except Exception:
        page.wait_for_timeout(2000)


def replace_richtext(page, selector: str, html: str) -> None:
    _focus_clear(page, selector)
    _paste_html(page, html)


def replace_bullets(page, selector: str, bullets: list[str], as_paragraphs: bool = False) -> None:
    if not bullets:
        return
    _focus_clear(page, selector)
    if as_paragraphs:
        # Paragraph-root fallback: upGrad keeps raw <strong> in <p> but may
        # strip it from <ul>/<li>. Loses the bullet glyph; preserves bold.
        html = "".join(f"<p>{b}</p>" for b in bullets)
    else:
        html = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
    _paste_html(page, html)


def _wait_for_save(page, prev_ts: str | None) -> str | None:
    """Block briefly until the 'Saved at HH:MM' indicator changes."""
    frame = app(page)
    ts_loc = frame.locator('span:has-text("Saved at")').first
    if ts_loc.count() == 0:
        page.wait_for_timeout(1200)
        return prev_ts
    for _ in range(24):  # ~12s
        try:
            cur = ts_loc.inner_text().strip()
        except Exception:
            cur = ""
        if cur and cur != prev_ts:
            return cur
        page.wait_for_timeout(500)
    return prev_ts


def _skills_html(skills: list[tuple[str, list[str]]]) -> str:
    """Render the 3-subgroup skills block. Each sub-heading is a plain
    paragraph (matches the existing master layout in the editor)."""
    parts = []
    for heading, items in skills:
        parts.append(f"<p>{heading}</p>")
        parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
    return "".join(parts)


def stage_edit(page, slug: str, as_paragraphs: bool = False) -> None:
    """Apply all per-slug tailoring from upgrad_resume.html into the editor."""
    data = parse_slug(slug)
    # Safety: a placeholder upgrad_resume.html (empty content) would silently
    # leave the editor as master and mark status='resume_finalized'. Refuse.
    if not data["headline"] and not data["summary"] and not data["experience"]:
        raise SystemExit(
            f"[edit] {slug}: upgrad_resume.html is empty/placeholder "
            f"(no headline, summary, or experience). Skipping. Author the full "
            f"upgrad_resume.html (14-section contract) first."
        )
    _suppress_chatgpt_buttons(page)
    last_save: str | None = None

    sections: list[tuple[str, str, callable]] = []  # (label, selector, applier)

    # NOTE: headline is intentionally LAST. Editing #personal_title_1 opens a
    # modal ("Personal Information") that intercepts pointer events for the
    # rest of the page. Running it last avoids that interference for the
    # other sections.
    if data["summary"]:
        sections.append((
            "summary",
            f"#SUM-child-0 {BODY}",
            lambda sel: replace_richtext(page, sel, f"<p>{data['summary']}</p>"),
        ))
    if data["skills"]:
        sections.append((
            "skills",
            f"#KS-child-0 {BODY}",
            lambda sel: replace_richtext(page, sel, _skills_html(data["skills"])),
        ))
    for idx, entry in enumerate(data["experience"]):
        sections.append((
            f"experience[{idx}]:{entry['key']}",
            f"#PR-child-{idx} {BODY}",
            lambda sel, e=entry: replace_bullets(page, sel, e["bullets"], as_paragraphs),
        ))
    if data["headline"]:
        sections.append((
            "headline",
            HEADLINE_FIELD,
            lambda sel: replace_headline_via_modal(page, data["headline"]),
        ))

    print(f"[edit] {len(sections)} section(s) to apply for {slug!r}", file=sys.stderr)
    for label, selector, apply in sections:
        print(f"[edit]   {label} -> {selector}", file=sys.stderr)
        try:
            apply(selector)
        except Exception as e:
            fail(page, f"edit-{label}", f"failed to apply {label}: {e!r}")
        last_save = _wait_for_save(page, last_save)
        print(f"[edit]     OK (saved {last_save!r})", file=sys.stderr)
    dump(page, "06b-after-edits")
    print("[edit] OK -- all sections applied", file=sys.stderr)


def stage_score(page) -> int | None:
    """Read the Resume Review aggregate score from the side panel."""
    print("[score] waiting for Resume Review score", file=sys.stderr)
    frame = app(page)
    score_span = frame.locator("span.score").first
    if score_span.count() == 0:
        print("[score]   no span.score in iframe", file=sys.stderr)
        return None
    # The score is computed async with a loading spinner; poll until a number
    # appears before "/100".
    score = None
    for _ in range(20):
        try:
            text = score_span.inner_text().strip()
        except Exception:
            text = ""
        m = re.search(r"(\d{1,3})\s*/\s*100", text)
        if m:
            score = int(m.group(1))
            break
        page.wait_for_timeout(1500)
    if score is None:
        print("[score]   did not converge within 30s -- check editor manually", file=sys.stderr)
    else:
        print(f"[score] OK -- Resume Review: {score}/100", file=sys.stderr)
    shot(page, "07-score")
    return score


def _resolve_slug_dir(slug: str) -> Path | None:
    """Find an app's on-disk workspace dir, supporting all layouts:

      root-level:  <repo>/<slug>/
      dated group: <repo>/<Month-YYYY>/<DD>/<slug>/   (current)
                   <repo>/<DD-MM-YYYY>/<slug>/        (legacy)

    Ordering: candidates come from upgrad_resume_paste._slug_dir_candidates
    (new layout by date descending, then legacy dated by date descending, then
    root-level); dirs holding upgrad_resume.html win, and 2+ such dirs is
    ambiguous and raises.
    """
    candidates = _slug_dir_candidates(slug, ROOT)
    if not candidates:
        return None
    with_resume = [d for d in candidates if (d / "upgrad_resume.html").exists()]
    if len(with_resume) > 1:
        listing = "\n  ".join(str(d) for d in with_resume)
        raise SystemExit(
            f"ambiguous slug {slug!r}: upgrad_resume.html found in multiple "
            f"workspaces:\n  {listing}"
        )
    if with_resume:
        return with_resume[0]
    return candidates[0]


def slug_pdf_path(slug: str, output: str | None = None) -> Path:
    """Per-app tailored resume PDF target. With --output, use that path;
    otherwise <workspace>/Abhisheik_Deo_Resume.pdf (root-level or dated)."""
    if output:
        return Path(output).expanduser().resolve()
    resolved = _resolve_slug_dir(slug)
    if resolved is None:
        raise SystemExit(f"slug dir not found (root-level or dated): {slug}")
    return resolved / "Abhisheik_Deo_Resume.pdf"


def stage_export(page, slug: str, output: str | None = None) -> Path | None:
    """Three-click flow:
      1. #resumeDownloadButton (Preview & Download) opens the preview modal
      2. .preview-download-btn opens the download-format options
      3. button:has-text('Download PDF') fires the actual PDF download
    """
    print("[export] clicking Preview & Download", file=sys.stderr)
    frame = app(page)
    btn = frame.locator("button#resumeDownloadButton").first
    if btn.count() == 0:
        fail(page, "export", "no button#resumeDownloadButton in iframe")
    target = slug_pdf_path(slug, output)
    target.parent.mkdir(parents=True, exist_ok=True)

    btn.click(timeout=5000)
    dl_btn = frame.locator("button.preview-download-btn").first
    try:
        dl_btn.wait_for(state="visible", timeout=15_000)
    except Exception as e:
        fail(page, "export", f"preview-download-btn never appeared: {e!r}")
    dl_btn.click(timeout=5000)
    # Now the format dropdown should render with "Download PDF" and "Download Word"
    pdf_btn = frame.locator('button:has-text("Download PDF")').first
    try:
        pdf_btn.wait_for(state="visible", timeout=10_000)
    except Exception as e:
        fail(page, "export", f"Download PDF option did not appear: {e!r}")
    try:
        with page.expect_download(timeout=60_000) as dl_info:
            pdf_btn.click(timeout=5000)
        download = dl_info.value
        download.save_as(str(target))
    except Exception as e:
        fail(page, "export", f"PDF download did not fire: {e!r}")
    try:
        rel = target.relative_to(ROOT)
    except ValueError:
        rel = target
    print(f"[export] OK -- saved {rel}", file=sys.stderr)
    return target


def _pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF, lower-cased and whitespace-normalized."""
    import pypdf
    reader = pypdf.PdfReader(str(pdf_path))
    parts = [page.extract_text() or "" for page in reader.pages]
    raw = " ".join(parts).lower()
    return re.sub(r"\s+", " ", raw)


def _normalize(s: str) -> str:
    """Strip HTML tags + entities + whitespace; lower-case. Used to make
    'expected' text from upgrad_resume.html comparable to PDF-extracted text."""
    import html as _html
    no_tags = re.sub(r"<[^>]+>", "", s)
    decoded = _html.unescape(no_tags)
    return re.sub(r"\s+", " ", decoded).strip().lower()


def _expected_fragments(data: dict) -> list[tuple[str, str]]:
    """Build (label, text) pairs of every fragment the PDF must contain.
    Bullets are checked individually so a single missing line is loud."""
    out: list[tuple[str, str]] = []
    if data["headline"]:
        out.append(("headline", _normalize(data["headline"])))
    if data["summary"]:
        out.append(("summary[first 60 chars]", _normalize(data["summary"])[:60]))
    for heading, items in data["skills"]:
        for i, it in enumerate(items):
            out.append((f"skills[{heading}][{i}]", _normalize(it)))
    for ei, entry in enumerate(data["experience"]):
        for bi, b in enumerate(entry["bullets"]):
            out.append((f"experience[{ei}:{entry['key']}][{bi}]",
                        _normalize(b)[:60]))
    return out


def stage_verify(slug: str, pdf_path: Path) -> None:
    """Read the downloaded PDF; assert every expected text fragment from
    upgrad_resume.html is present. If anything is missing, dump a report
    and raise -- the summary stage won't run.
    """
    try:
        rel = pdf_path.relative_to(ROOT)
    except ValueError:
        rel = pdf_path
    print(f"[verify] checking {rel}", file=sys.stderr)
    if not pdf_path.exists():
        raise SystemExit(f"[verify] PDF not at expected path: {pdf_path}")
    pdf_text = _pdf_text(pdf_path)
    data = parse_slug(slug)
    fragments = _expected_fragments(data)

    missing: list[tuple[str, str]] = []
    for label, needle in fragments:
        if not needle:
            continue
        # Match needle against normalized pdf_text. Allow some flexibility
        # by also trying with em-dash variants and en-dash variants normalised.
        candidates = {needle, needle.replace("—", "-"), needle.replace("–", "-")}
        if not any(c in pdf_text for c in candidates):
            missing.append((label, needle))

    report_path = DEBUG_DIR / f"verify-{slug}.txt"
    lines = [
        f"slug: {slug}",
        f"pdf: {pdf_path}",
        f"total fragments checked: {len(fragments)}",
        f"missing: {len(missing)}",
        "",
    ]
    for label, needle in missing:
        lines.append(f"  MISSING  {label}: {needle[:120]!r}")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  report: {report_path.relative_to(ROOT)}", file=sys.stderr)

    if missing:
        raise SystemExit(
            f"[verify] {len(missing)}/{len(fragments)} fragments missing from PDF; "
            f"see {report_path.relative_to(ROOT)}"
        )
    print(f"[verify] OK -- all {len(fragments)} fragments present", file=sys.stderr)


def stage_summary(slug: str, score: int | None, pdf_path: Path, verify_ok: bool) -> None:
    """Print a JSON result + write _upgrad_run.json to the workspace.

    No database: status is tracked via the workspace index.html pills and the
    in-flight memory file, updated separately. 'resume_finalized' means the
    resume is pasted into upGrad, ATS-scored, exported, and verified — not yet
    submitted to the company's career ATS.
    """
    summary = {
        "slug": slug,
        "ats_resume_score": score,
        "pdf": str(pdf_path),
        "verify_ok": verify_ok,
        "status": "resume_finalized",
    }
    print(json.dumps(summary))  # stdout = machine-readable result

    resolved = _resolve_slug_dir(slug)
    if resolved is not None:
        sidecar = resolved / "_upgrad_run.json"
        sidecar.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        try:
            rel = sidecar.relative_to(ROOT)
        except ValueError:
            rel = sidecar
        print(f"[summary] wrote {rel}", file=sys.stderr)
    print(
        f"[summary] OK -- score={score} verify_ok={verify_ok} pdf={pdf_path}",
        file=sys.stderr,
    )


def run_one(
    page,
    slug: str,
    stop_idx: int,
    no_pause: bool,
    reset: bool,
    master_title: str,
    output: str | None,
    as_paragraphs: bool,
) -> None:
    """Run the full per-slug flow up to the chosen stop stage."""
    slug_dir = _resolve_slug_dir(slug)
    if slug_dir is None:
        raise SystemExit(f"slug dir not found (root-level or dated): {slug}")

    def between(after_stage: str) -> None:
        if no_pause or STAGES.index(after_stage) == stop_idx:
            return
        prompt(f"finished stage {after_stage!r} -- Enter for next, Ctrl+C to stop here")

    # login/nav are idempotent; on second+ run they no-op fast.
    stage_login(page)
    if stop_idx == 0:
        return
    between("login")

    stage_nav(page)
    if stop_idx == 1:
        return
    between("nav")

    stage_find_master(page, master_title)
    if stop_idx == 2:
        return
    between("find-master")

    new_name = stage_clone(page, slug, master_title, reset=reset)
    if stop_idx == 3:
        return
    between("clone")

    stage_open_copy(page, new_name)
    if stop_idx == 4:
        return
    between("open-copy")

    stage_edit(page, slug, as_paragraphs)
    if stop_idx == 5:
        return
    between("edit")

    score = stage_score(page)
    if stop_idx == 6:
        return
    between("score")

    pdf_path = stage_export(page, slug, output)
    if stop_idx == 7:
        return
    between("export")

    stage_verify(slug, pdf_path)
    if stop_idx == 8:
        return
    between("verify")

    stage_summary(slug, score, pdf_path, True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="workspace <slug> to apply for")
    ap.add_argument(
        "--stop-after",
        choices=STAGES,
        default="summary",
        help="stop after this stage (inclusive)",
    )
    ap.add_argument("--output", default=None,
                    help="PDF output path override (default <workspace>/Abhisheik_Deo_Resume.pdf)")
    ap.add_argument("--master", default=MASTER_TITLE,
                    help=f"master resume card title (default {MASTER_TITLE!r}; "
                         f"env UPGRAD_MASTER_CARD overrides the default)")
    ap.add_argument("--bullets-as-paragraphs", action="store_true",
                    help="paste experience bullets as <p> instead of <ul><li> "
                         "(fallback if list paste strips bold)")
    ap.add_argument("--no-pause", action="store_true", help="don't pause between stages")
    ap.add_argument("--reset", action="store_true",
                    help="delete existing <slug>_ats_resume in upGrad first (start fresh)")
    ap.add_argument("--slow", type=int, default=0, help="Playwright slow_mo ms")
    args = ap.parse_args()

    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    stop_idx = STAGES.index(args.stop_after)

    with headed_context(slow_mo_ms=args.slow) as ctx:
        page = ctx.new_page()
        print(f"\n[run] {args.slug}", file=sys.stderr)
        run_one(
            page,
            args.slug,
            stop_idx,
            args.no_pause,
            reset=args.reset,
            master_title=args.master,
            output=args.output,
            as_paragraphs=args.bullets_as_paragraphs,
        )
        print("\n[done]", file=sys.stderr)


if __name__ == "__main__":
    main()
