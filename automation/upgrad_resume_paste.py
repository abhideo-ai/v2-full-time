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


def _block_elements(div) -> list:
    """The bullet elements of a section, in order.

    Accepts BOTH shapes, because one file now serves two masters:

      <ul><li>…</li></ul>   the original machine-facing shape
      <p>…</p><p>…</p>      standalone paragraphs

    The paragraph form exists because upGrad's paste sanitiser STRIPS BOLD from
    list-rooted content, so anything a human copies by hand must not sit inside
    a <ul>. Supporting both here is what allows a single résumé file to be both
    hand-pasted and bot-parsed, instead of two files that silently drift apart.

    Returning [] on an unrecognised shape would be silently skipped by the
    callers, so an unparseable section must look empty ONLY when it truly is.

    ⚠ This is the ONE definition of "what counts as a bullet". `_ul_items_html`
    (the exporter's path) and `parse_sections` (the `resume_bullets` index)
    both go through it, so the table can never disagree with what the bot
    writes about how a section splits into lines.
    """
    ul = div.find("ul")
    if ul is not None:
        return list(ul.find_all("li", recursive=False))
    return [p for p in div.find_all("p", recursive=False) if p.get_text(strip=True)]


def _ul_items_html(div) -> list[str]:
    """Each bullet's inner HTML, <strong>/<em> preserved."""
    return [_inner_html(el) for el in _block_elements(div)]


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


# ---------------------------------------------------------------------------
# The whole file, section by section — the source of the `resume_bullets` index
# ---------------------------------------------------------------------------
# `parse_resume_paste` above answers "what does the bot paste into Hiration?",
# so it returns the TEN parsed sections in the editor's own shape and ignores
# everything else. This second view answers a different question — "what does
# this résumé actually SAY?" — so it walks all FIFTEEN sections, including the
# five pre-2016 roles the exporter never touches.
#
# Those five matter here and nowhere else: CLAUDE.md's verb-uniqueness rule is
# explicitly "check across ALL TEN roles, not just the five parsed ones", and
# missing that once put `Hardened` in both VoltusWave and El Paso.
#
# Both views share `_section_div` and `_block_elements`, so this is a second
# QUESTION asked of one parser, not a second parser.

# Section id -> kind, in file order. `experience` entries are positional: the
# Nth of them is row N of the résumé's own dates table (see `role_table`).
SECTION_ORDER: list[tuple[str, str]] = [
    ("quick-headline",              "headline"),
    ("quick-summary",               "summary"),
    ("quick-skills-tls",            "skills"),
    ("quick-skills-ee",             "skills"),
    ("quick-skills-bd",             "skills"),
    ("quick-vp",                    "experience"),
    ("quick-deque",                 "experience"),
    ("quick-rocket",                "experience"),
    ("quick-voltuswave-cofounder",  "experience"),
    ("quick-teletext",              "experience"),
    ("p-cura",                      "experience"),
    ("p-innroad",                   "experience"),
    ("p-mcd",                       "experience"),
    ("p-elpaso",                    "experience"),
    ("p-lynton",                    "experience"),
]

SECTION_KINDS = sorted({kind for _, kind in SECTION_ORDER})

# The five the exporter never writes. They live in the Hiration card and are
# hand-edited there; a renderer building a paste sheet must not offer them, and
# a renderer building a Word CV must include them. Hence the flag.
CARD_ONLY_IDS = {sec_id for sec_id, _ in SECTION_ORDER if sec_id.startswith("p-")}

_LEADING_NUM_RE = re.compile(r"^\s*\d+\.\s*")


def _norm(value: str) -> str:
    return " ".join(value.split())


def _cell(el) -> str:
    """Plain text of an element: tags dropped, entities unescaped, spaces collapsed.

    ⚠ No separator between children. `get_text(" ")` inserts one at every tag
    boundary, which turns `<strong>P95 under 16 ms</strong>,` into "16 ms ," —
    wrong in a plain-text render, and it inflates `word_count` past the ≤25-word
    hygiene rule by counting the orphaned comma. The file already carries its
    spacing outside the tags.
    """
    return _norm(el.get_text())


def _heading(div) -> str | None:
    """The section's own <h2>, with its leading `N. ` stripped.

    Verbatim otherwise — including the trailing `— card-only` the file writes on
    sections 11-15. It is the file's wording, and rewriting it here would be the
    derived layer editorialising over its source.
    """
    h2 = div.find_previous("h2")
    return _LEADING_NUM_RE.sub("", _cell(h2)) if h2 else None


def role_table(soup: BeautifulSoup) -> list[dict]:
    """The résumé's own `#  Employer  Title  From  To  Location` table.

    This is what lets `section_id='quick-vp'` read back as "VoltusWave
    Technologies — Principal Software Architect (Mar 2025 – Apr 2026)".

    ⚠ These dates are what the file ASSERTS. The dates that reach an exported
    PDF live in the Hiration card, which is why the table's own heading says
    "verify, do not assume the clone kept them". For a locally rendered CV this
    table is the only date source there is.

    Rows are identified by shape — six cells, the first a row number — so the
    Personal Information table sitting in the same document is not mistaken for
    a role.
    """
    rows = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) != 6 or not _cell(cells[0]).isdigit():
            continue
        rows.append({
            "n":          int(_cell(cells[0])),
            "company":    _cell(cells[1]),
            "role_title": _cell(cells[2]),
            "date_from":  _cell(cells[3]),
            "date_to":    _cell(cells[4]),
            "location":   _cell(cells[5]),
        })
    rows.sort(key=lambda r: r["n"])
    return rows


def parse_sections(path: Path) -> dict:
    """Every section of one résumé file, in file order.

    {
      "roles":   [ {n, company, role_title, date_from, date_to, location}, ... ],
      "missing": ["p-lynton", ...],          # ids in SECTION_ORDER with no div
      "sections": [
        {"id", "kind", "label", "card_only", "role": {...}|None,
         "blocks": [{"html": str, "text": str}, ...]},
        ...
      ],
    }

    A section whose id is absent or misspelt lands in `missing` rather than
    vanishing. `master/README.md` calls that the silent trap — the export still
    looks successful — so the one reader that walks the whole file says so.
    """
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    roles = role_table(soup)
    by_n = {r["n"]: r for r in roles}

    sections, missing, seen_experience = [], [], 0
    for sec_id, kind in SECTION_ORDER:
        div = _section_div(soup, sec_id)
        role = None
        if kind == "experience":
            seen_experience += 1
            role = by_n.get(seen_experience)
        if div is None:
            missing.append(sec_id)
            continue
        sections.append({
            "id":        sec_id,
            "kind":      kind,
            "label":     _heading(div),
            "card_only": sec_id in CARD_ONLY_IDS,
            "role":      role,
            "blocks":    [{"html": _inner_html(el), "text": _cell(el)}
                          for el in _block_elements(div)],
        })
    return {"roles": roles, "sections": sections, "missing": missing}


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
