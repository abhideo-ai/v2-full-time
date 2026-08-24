"""Parse <slug>/upgrad_resume.html into structured sections.

upgrad_resume.html is the COMPLETE tailored resume for one application, in
final order across the named sections the upGrad editor consumes
(quick-headline, quick-summary, quick-skills-tls/ee/bd,
quick-vp/deque/rocket/voltuswave-cofounder/teletext). It is authored per
workspace (see CLAUDE.md "Automated upGrad resume build").

Each section is `<div class="section copy-target" id="quick-<name>">`
containing a `<button class="copy-btn">...</button>` plus the rendered
content (either a `<p>` for prose or `<ul><li>` for bullets).

We strip the button and return the structured content for the upGrad
editor automation to paste.

Output schema:
{
  "headline":  str,                         # plain text
  "summary":   str,                         # HTML with <strong> preserved
  "skills":    list[tuple[str, list[str]]], # [(heading, [items, ...]), ...]
  "experience": list[dict],                 # [{"key", "bullets": [str_html, ...]}, ...]
                                            # order: vp, deque, rocket, cofounder, teletext
}
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

# Order of experience sections in the editor (PR-child-0..4) and in
# upgrad_resume.html. Master template is built in this order.
EXPERIENCE_KEYS = ["vp", "deque", "rocket", "voltuswave-cofounder", "teletext"]

SKILLS_SUBGROUPS = [
    ("Technology Leadership & Strategy", "quick-skills-tls"),
    ("Engineering Excellence",           "quick-skills-ee"),
    ("Business & Delivery",              "quick-skills-bd"),
]


def _inner_html(el) -> str:
    """Stringify the children of `el` (no enclosing tag)."""
    return "".join(str(c) for c in el.children).strip()


def _ul_items_html(div) -> list[str]:
    """Return each <li>'s inner HTML (with <strong>/<em> preserved)."""
    ul = div.find("ul")
    if ul is None:
        return []
    return [_inner_html(li) for li in ul.find_all("li", recursive=False)]


def _section_div(soup: BeautifulSoup, sec_id: str):
    div = soup.select_one(f"#{sec_id}")
    if div is None:
        return None
    # Drop the copy button so the section body is clean
    for btn in div.select(".copy-btn"):
        btn.decompose()
    return div


def parse_resume_paste(resume_paste_path: Path) -> dict:
    soup = BeautifulSoup(resume_paste_path.read_text(encoding="utf-8"), "html.parser")

    def text_of(sec_id: str) -> str:
        div = _section_div(soup, sec_id)
        if div is None:
            return ""
        p = div.find("p")
        return p.get_text(strip=True) if p else div.get_text(strip=True)

    def html_of_paragraph(sec_id: str) -> str:
        div = _section_div(soup, sec_id)
        if div is None:
            return ""
        p = div.find("p")
        return _inner_html(p) if p else _inner_html(div)

    def bullets_of(sec_id: str) -> list[str]:
        div = _section_div(soup, sec_id)
        return _ul_items_html(div) if div else []

    skills: list[tuple[str, list[str]]] = []
    for heading, sec_id in SKILLS_SUBGROUPS:
        items = bullets_of(sec_id)
        if items:
            skills.append((heading, items))

    experience = []
    for key in EXPERIENCE_KEYS:
        bullets = bullets_of(f"quick-{key}")
        if bullets:
            experience.append({"key": key, "bullets": bullets})

    return {
        "headline":   text_of("quick-headline"),
        "summary":    html_of_paragraph("quick-summary"),
        "skills":     skills,
        "experience": experience,
    }


_DATED_DIR_RE = re.compile(r"^\d{2}-(\d{2}|[A-Za-z]+)-\d{4}$")
_MONTH_DIR_RE = re.compile(r"^[A-Z][a-z]+-\d{4}$")
_DAY_DIR_RE = re.compile(r"^\d{2}$")


def _parse_dated_dir(name: str) -> datetime:
    """`DD-MM-YYYY` / `DD-Month-YYYY` -> datetime (datetime.min if unparseable)."""
    for fmt in ("%d-%m-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(name, fmt)
        except ValueError:
            continue
    return datetime.min


def _parse_month_day(month_name: str, day_name: str) -> datetime:
    """`Month-YYYY` + `DD` -> datetime (datetime.min if unparseable)."""
    try:
        return datetime.strptime(f"{day_name}-{month_name}", "%d-%B-%Y")
    except ValueError:
        return datetime.min


def _slug_dir_candidates(slug: str, root: Path) -> list[Path]:
    """ALL workspace dirs matching `slug` across the three layouts, in
    deterministic resolution order: new-layout <Month-YYYY>/<DD> dirs by
    parsed date descending, then legacy <DD-MM-YYYY>/<DD-Month-YYYY> dirs
    by parsed date descending, then the root-level dir last."""
    new_layout: list[tuple[datetime, Path]] = []
    legacy: list[tuple[datetime, Path]] = []
    for sub in root.iterdir():
        if not sub.is_dir():
            continue
        if _DATED_DIR_RE.match(sub.name):
            candidate = sub / slug
            if candidate.is_dir():
                legacy.append((_parse_dated_dir(sub.name), candidate))
        elif _MONTH_DIR_RE.match(sub.name):
            for day in sub.iterdir():
                if day.is_dir() and _DAY_DIR_RE.match(day.name):
                    candidate = day / slug
                    if candidate.is_dir():
                        new_layout.append((_parse_month_day(sub.name, day.name), candidate))
    new_layout.sort(key=lambda t: (t[0], t[1].as_posix()), reverse=True)
    legacy.sort(key=lambda t: (t[0], t[1].as_posix()), reverse=True)
    ordered = [p for _, p in new_layout] + [p for _, p in legacy]
    direct = root / slug
    if direct.is_dir():
        ordered.append(direct)
    return ordered


def _resolve_resume_paste(slug: str, root: Path) -> Path:
    """Find upgrad_resume.html supporting all layouts:
      <root>/<slug>/upgrad_resume.html                     (root-level workspace)
      <root>/<Month-YYYY>/<DD>/<slug>/upgrad_resume.html   (current dated group)
      <root>/<DD-MM-YYYY>/<slug>/upgrad_resume.html        (legacy dated group)

    Ordering: all candidate dirs are collected via _slug_dir_candidates (new
    layout by date descending, then legacy dated by date descending, then
    root-level); 2+ dirs holding upgrad_resume.html is ambiguous and raises.
    """
    with_resume = [
        d / "upgrad_resume.html"
        for d in _slug_dir_candidates(slug, root)
        if (d / "upgrad_resume.html").exists()
    ]
    if len(with_resume) > 1:
        listing = "\n  ".join(str(p) for p in with_resume)
        raise SystemExit(
            f"ambiguous slug {slug!r}: upgrad_resume.html found in multiple "
            f"workspaces:\n  {listing}"
        )
    if with_resume:
        return with_resume[0]
    # so the FileNotFoundError below cites the root-level path
    return root / slug / "upgrad_resume.html"


def parse_slug(slug: str, root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parent.parent
    path = _resolve_resume_paste(slug, root)
    if not path.exists():
        raise FileNotFoundError(
            f"upgrad_resume.html not found (root-level or dated): {slug}"
        )
    return parse_resume_paste(path)
