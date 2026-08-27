#!/usr/bin/env python3
"""The master résumé as a Word document, rendered from `jobs_tracker_v2`.

    JOBS_TRACKER_DSN=dbname=jobs_tracker_v2   (default)

⚑ .docx IS THE CANONICAL OUTPUT NOW. His words, 2026-08-27: "for resumes, we can
create docx. right? wouldn't that be easier?" … "we create .docx file(s) that I
can also edit easily." … "that's going to be our form now." … "No need of a HTML
page or anything."

    resume_documents + resume_roles + resume_education + resume_profile
    + resume_sections + resume_blocks                          ← AUTHORED
                |
                +--> resume_docx.py generate --> master/Abhisheik_Deo_Resume.docx
                |                                        --> he edits it in Word
                +--> resume_db.py generate --> master/upgrad_resume.generated.html
                                                  ^ ROUND-TRIP PROOF, not a deliverable

This module is a SIBLING of `resume_db.py`, not a replacement. `resume_db.py`
still renders the HTML that proves the database reproduces the master file
byte-for-byte; that gate is what makes trusting these tables safe. This module
renders the same tables to the thing he actually sends. Neither writes
`master/upgrad_resume.html`.

⛔ WHY EVERY WORD COMES OUT OF THE DATABASE.
CLAUDE.md: "Generate copy blocks FROM the résumé, never retype them." Retyping is
how six copies of his career diverged. Nothing here composes a sentence: bullets,
skills, headline, summary, role titles, dates, locations, education and contact
details are all SELECTed. The one string this module supplies is CANDIDATE_NAME
below, and it is flagged there because it is identity, not a claim.

⛔ WHY THE ORDERING IS `resume_sections.ord`, NEVER `section_id`.
`resume_db.render()` selects blocks `ORDER BY section_id, ord`, which is
alphabetical. That is safe THERE only because it immediately regroups the rows
into a dict and lets the ordered `sections` list drive emission. Copying that
query and iterating it directly opens the résumé with the five card-only pre-2016
roles and buries the headline at position 7 — and every count-based check still
passes, because nothing is missing. Order by `s.ord, b.ord` or the document is
wrong in a way that looks right.

⛔ WHY `retired_at IS NULL` SITS IN THE JOIN, NOT THE `WHERE`.
"A bullet LEAVES the master by being retired, never by being deleted"
(migration 012). There are zero retired bullets today, so forgetting the filter
passes now and corrupts later — and `resume_db.load_from()` re-inserts carried
retired bullets at `max(ord)+1` INSIDE their own section, so a stale bullet lands
at the tail of the correct role reading like a real one. In a `WHERE` clause the
filter also degrades the LEFT JOIN to an inner join, and a section whose blocks
were all retired would lose its heading, company and dates entirely.

⛔ WHY BOLD IS THE PASS/FAIL CONDITION.
`resume-issues-to-avoid/README.md` rule 9: bold silently stripped on export makes
the ATS read every bullet as having no highlighted fact and "score craters even
though the source HTML is hygienically correct" — and it was not noticed until an
exported PDF. `<strong>` is not decoration here; it is the bolded fact the
hygiene rules require on every bullet. So `generate` REFUSES to write a document
whose bold spans do not match the database exactly, and `verify` re-opens the
saved file and proves it again from disk.

    resume_docx.py generate [--out P]   render the DB to a .docx
    resume_docx.py verify   [--out P]   re-open that .docx and prove it from the DB

Sibling of `jobs_db.py` / `resume_db.py`: same connection pattern, raw SQL, dict
rows, no ORM. python-docx builds the file and does nothing else.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import pathlib
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

DSN = os.environ.get("JOBS_TRACKER_DSN", "dbname=jobs_tracker_v2")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "master" / "Abhisheik_Deo_Resume.docx"
DOC_KEY = "master"

# ⚑ THE ONE STRING NOT IN THE DATABASE. `resume_documents` has no name column and
# master/upgrad_resume.html never carried one — the Hiration card supplied it.
# A name is identity, not a claim, so it is stated here in the open rather than
# smuggled in, and it is the only literal on the page. Everything else is SELECTed.
CANDIDATE_NAME = "Abhisheik Deo"

# ⛔ The ten ids the résumé cannot be missing. Same list as `resume_db.CONTRACT_IDS`,
# imported so the two can never drift.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from resume_db import CONTRACT_IDS  # noqa: E402

# A4, not python-docx's US-Letter default: he is in Hyderabad applying largely to
# India-based seats. One line to flip if that ever stops being true.
PAGE_W, PAGE_H = Inches(8.27), Inches(11.69)
MARGIN_TB, MARGIN_LR = Inches(0.5), Inches(0.6)
BASE_FONT, BASE_SIZE = "Calibri", Pt(10.5)

LINKEDIN_PREFIX = "linkedin.com/in/"
LINKEDIN_URL = "https://www.linkedin.com/in/"

# The named entities the master uses — the same set `resume_db.KNOWN_ENTITIES`
# guards. `html.unescape()` is deliberately NOT used: it resolves the whole HTML5
# reference table plus semicolon-less legacy forms, so a typo like `&emdash;`
# would silently become something instead of failing loudly. Expand `&amp;` LAST
# so `&amp;lt;` cannot turn into a real `<`.
ENTITIES = [("&lt;", "<"), ("&gt;", ">"), ("&mdash;", "—"), ("&ndash;", "–"),
            ("&nbsp;", " "), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")]
RE_ENTITY = re.compile(r"&#?[A-Za-z0-9]+;")
RE_STRONG = re.compile(r"(</?strong>)")
RE_SKILLS_PREFIX = re.compile(r"^Skills\s*[—–-]\s*")


class BuildError(RuntimeError):
    """The data is not the shape this module knows. Never guessed around."""


# ---------------------------------------------------------------------------
# Inline markup — split on tags FIRST, unescape each run SECOND
# ---------------------------------------------------------------------------
# Order matters and is not cosmetic. 10 of the 16 entities in the master sit
# INSIDE a <strong> (`<strong>25&ndash;30%</strong>`), and unescaping the whole
# string first is the injection `resume_db.py`'s docstring names: `&lt;strong&gt;`
# would become a real tag. Split, then unescape the pieces.

def unescape(text: str) -> str:
    for entity, char in ENTITIES:
        text = text.replace(entity, char)
    stray = RE_ENTITY.search(text)
    if stray:
        raise BuildError(f"unknown HTML entity {stray.group(0)!r} in {text!r}")
    return text


def inline_runs(html: str) -> list[tuple[str, bool]]:
    """`<strong>`-aware split into (text, bold) runs.

    Refuses anything that is not plain text or a balanced <strong>. The master's
    91 live blocks contain exactly one construct — `<strong>` — with no
    attributes and no nesting, so an unrecognised tag is a change to the data
    this module has not been told about, not something to unwrap silently.
    """
    runs: list[tuple[str, bool]] = []
    bold = False
    for piece in RE_STRONG.split(html):
        if piece == "<strong>":
            if bold:
                raise BuildError(f"nested <strong> in {html!r}")
            bold = True
            continue
        if piece == "</strong>":
            if not bold:
                raise BuildError(f"unbalanced </strong> in {html!r}")
            bold = False
            continue
        if not piece:
            continue
        if "<" in piece or ">" in piece:
            raise BuildError(f"unexpected markup {piece!r} in {html!r}")
        runs.append((unescape(piece), bold))
    if bold:
        raise BuildError(f"unclosed <strong> in {html!r}")
    return runs


def strong_spans(html: str) -> list[str]:
    """The bolded facts, in order — what must survive into the .docx."""
    return [text for text, bold in inline_runs(html) if bold]


# ---------------------------------------------------------------------------
# fetch — the whole document, in render order, in one place
# ---------------------------------------------------------------------------

def fetch() -> dict:
    with psycopg.connect(DSN, row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM resume_documents WHERE doc_key = %s", (DOC_KEY,))
        doc = cur.fetchone()
        if doc is None:
            raise BuildError(f"no document {DOC_KEY!r} in {DSN} — run `resume_db.py load`")

        cur.execute("SELECT * FROM resume_profile WHERE doc_key=%s ORDER BY ord", (DOC_KEY,))
        profile = cur.fetchall()
        cur.execute("SELECT * FROM resume_education WHERE doc_key=%s ORDER BY ord", (DOC_KEY,))
        education = cur.fetchall()
        cur.execute("""SELECT * FROM resume_certifications WHERE doc_key=%s ORDER BY ord""",
                    (DOC_KEY,))
        certifications = cur.fetchall()

        # ⛔ ORDER BY s.ord, b.ord — see the module docstring. And `retired_at IS
        # NULL` in the JOIN's ON clause, never in the WHERE.
        cur.execute("""
            SELECT s.ord AS section_ord, s.section_id, s.section_kind, s.card_only,
                   s.heading_html, s.role_n,
                   r.company, r.role_title, r.date_from, r.date_to, r.location,
                   r.date_to_emphasised,
                   b.ord AS block_ord, b.bullet_key, b.html, b.text
              FROM resume_sections s
              LEFT JOIN resume_roles  r ON r.doc_key = s.doc_key AND r.n = s.role_n
              LEFT JOIN resume_blocks b ON b.doc_key = s.doc_key
                                       AND b.section_id = s.section_id
                                       AND b.retired_at IS NULL
             WHERE s.doc_key = %s
             ORDER BY s.ord, b.ord
        """, (DOC_KEY,))
        rows = cur.fetchall()

    sections: list[dict] = []
    for row in rows:
        if not sections or sections[-1]["section_id"] != row["section_id"]:
            sections.append({
                "ord": row["section_ord"], "section_id": row["section_id"],
                "kind": row["section_kind"], "card_only": row["card_only"],
                "heading": unescape(row["heading_html"]), "role_n": row["role_n"],
                "company": row["company"], "role_title": row["role_title"],
                "date_from": row["date_from"], "date_to": row["date_to"],
                "location": row["location"],
                "date_to_emphasised": row["date_to_emphasised"],
                "blocks": [],
            })
        if row["bullet_key"] is not None:
            sections[-1]["blocks"].append(
                {"ord": row["block_ord"], "key": row["bullet_key"],
                 "html": row["html"], "text": row["text"]})

    # ⛔ The contract, asserted before a byte is built. `resume_db.render()` makes
    # the same assertion for the same reason: an empty section is skipped
    # silently downstream and the export still reports success.
    by_id = {s["section_id"]: s for s in sections}
    broken = [i for i in CONTRACT_IDS if not by_id.get(i, {}).get("blocks")]
    if broken:
        raise BuildError(f"parser-contract sections missing or empty: {broken}")

    return {"doc": doc, "profile": profile, "education": education,
            "certifications": certifications, "sections": sections}


def contact(profile: list[dict]) -> list[tuple[str, bool, str | None]]:
    """The contact line as (text, bold, url) parts, from `resume_profile`.

    ⚠ The LinkedIn row's `value_text` is `abhisheikdeo — not abhideo, which is
    the email domain`. That trailing clause is a note to the reader of the HTML
    build artefact, not contact data, and it must never reach a résumé he sends.
    The slug alone is the row's single <strong>, so it is taken from there and
    the gloss cannot follow it.
    """
    fields = {row["field_label"]: row for row in profile}
    for label in ("Current location", "Phone", "Email", "LinkedIn slug"):
        if label not in fields:
            raise BuildError(f"resume_profile has no {label!r} row")

    # Pulled with a regex rather than through `inline_runs`, which refuses
    # anything but <strong>: this one row also carries a <code> tag, and that is
    # correct — the gloss around the slug is prose about the file, and the strict
    # parser refusing it is exactly the signal that it is not résumé content.
    slugs = re.findall(r"<strong>([^<]*)</strong>", fields["LinkedIn slug"]["value_html"])
    if len(slugs) != 1:
        raise BuildError(f"expected exactly one bolded LinkedIn slug, got {slugs!r}")
    slug = unescape(slugs[0])

    parts: list[tuple[str, bool, str | None]] = []
    for text, bold in inline_runs(fields["Current location"]["value_html"]):
        parts.append((text, bold, None))
    parts.append((" · " + fields["Phone"]["value_text"], False, None))
    parts.append((" · " + fields["Email"]["value_text"], False,
                  "mailto:" + fields["Email"]["value_text"]))
    parts.append((" · " + LINKEDIN_PREFIX, False, LINKEDIN_URL + slug))
    parts.append((slug, True, LINKEDIN_URL + slug))
    return parts


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def _pin_font(style, name: str) -> None:
    """Remove the inherited THEME font reference and pin a real face.

    `style.font.name = "Calibri"` leaves `w:asciiTheme` in place beside the
    explicit `w:ascii`, so the face Word actually uses depends on the theme. It
    is latent rather than active today (this template's major font IS Calibri),
    and it bites the moment anyone picks a different one. Pinning `w:eastAsia`
    and `w:cs` too stops Word substituting a fallback face for the stray glyphs
    this résumé is full of — the em and en dashes, the `·` separators, and the
    single Greek gamma in the Rosenbaum bullet, which sits inside a BOLD run
    where a silent substitution reads as "the bold looks wrong".
    """
    rf = style.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if qn(attr) in rf.attrib:
            del rf.attrib[qn(attr)]
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(attr), name)


def _drop_contextual_spacing(style) -> None:
    """`List Bullet` ships with `<w:contextualSpacing/>`, which makes any spacing
    set between consecutive bullets dead on arrival. python-docx does not expose
    it, so it comes out via lxml or the setting below is a no-op that reads as
    if it worked."""
    p_pr = style.element.get_or_add_pPr()
    found = p_pr.find(qn("w:contextualSpacing"))
    if found is not None:
        p_pr.remove(found)


def _style_document(document: Document) -> None:
    section = document.sections[0]
    section.page_width, section.page_height = PAGE_W, PAGE_H
    section.top_margin = section.bottom_margin = MARGIN_TB
    section.left_margin = section.right_margin = MARGIN_LR

    styles = document.styles
    normal = styles["Normal"]
    normal.font.size = BASE_SIZE
    _pin_font(normal, BASE_FONT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(3)
    # ⛔ python-docx's default template carries <w:spacing w:line="276"> in
    # docDefaults — 276/240 = 1.15 line spacing — and NOTHING here overrode it.
    # It applied to all 112 paragraphs, cost roughly half a page, and silently
    # defeated the deliberate Pt(0)/Pt(1)/Pt(2) spacing set below. Half a page
    # matters: the 3-page cap has never been verified at 64 bullets.
    normal.paragraph_format.line_spacing = 1.0

    h1 = styles["Heading 1"]                      # the name
    h1.font.size, h1.font.bold, h1.font.color.rgb = Pt(20), True, RGBColor(0, 0, 0)
    _pin_font(h1, BASE_FONT)
    h1.paragraph_format.space_before, h1.paragraph_format.space_after = Pt(0), Pt(2)

    h2 = styles["Heading 2"]                      # SUMMARY / KEY SKILLS / …
    h2.font.size, h2.font.bold, h2.font.color.rgb = Pt(11), True, RGBColor(0, 0, 0)
    h2.font.all_caps = True   # displays SUMMARY; the extracted text stays "Summary"
    _pin_font(h2, BASE_FONT)
    h2.paragraph_format.space_before, h2.paragraph_format.space_after = Pt(8), Pt(2)

    h3 = styles["Heading 3"]                      # a role, or a skills group
    h3.font.size, h3.font.bold, h3.font.color.rgb = Pt(10.5), False, RGBColor(0, 0, 0)
    _pin_font(h3, BASE_FONT)
    h3.paragraph_format.space_before, h3.paragraph_format.space_after = Pt(5), Pt(1)

    bullet = styles["List Bullet"]
    bullet.font.size = BASE_SIZE
    _pin_font(bullet, BASE_FONT)
    _drop_contextual_spacing(bullet)
    bullet.paragraph_format.left_indent = Inches(0.22)
    bullet.paragraph_format.first_line_indent = Inches(-0.22)
    bullet.paragraph_format.space_before, bullet.paragraph_format.space_after = Pt(0), Pt(1)

    # There is no built-in Hyperlink character style in python-docx's template.
    if "Hyperlink" not in [s.name for s in styles]:
        from docx.enum.style import WD_STYLE_TYPE
        link = styles.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
        link.font.color.rgb = RGBColor(0x0B, 0x4F, 0x9E)
        link.font.underline = True


def _add_runs(paragraph, runs: list[tuple[str, bool]]) -> None:
    for text, bold in runs:
        run = paragraph.add_run(text)
        # ⛔ Set bold ONLY when true. `run.bold = False` writes an explicit
        # <w:b w:val="0"/>, and direct formatting outranks the style — 299 of
        # them meant that editing "List Bullet" in Word's style pane did
        # NOTHING. Leaving it None inherits the style, which is what makes
        # the document editable.
        if bold:
            run.bold = True


def _add_hyperlink(paragraph, url: str, text: str, bold: bool) -> None:
    """python-docx 1.2 has no hyperlink API — `paragraph.hyperlinks` is read-only.

    Worth the hand-built element: CLAUDE.md's measurement traps record that the
    LinkedIn slug lived only in a PDF link annotation and a text-only grep read a
    perfectly good file as missing it. Here the slug is in BOTH the relationship
    target and the visible run text, so either check finds it.
    """
    r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    style = OxmlElement("w:rStyle")
    style.set(qn("w:val"), "Hyperlink")
    r_pr.append(style)
    if bold:
        r_pr.append(OxmlElement("w:b"))
    run.append(r_pr)
    node = OxmlElement("w:t")
    node.text = text
    node.set(qn("xml:space"), "preserve")
    run.append(node)
    link.append(run)
    paragraph._p.append(link)


def _role_heading(section: dict) -> list[tuple[str, bool]]:
    """company · title · dates · location, composed from `resume_roles`.

    NOT from `heading_html`: that column exists to reproduce the HTML build
    artefact byte-for-byte and carries its wording — `— card-only`, and
    `· THE JAVA YEARS` on El Paso. Both are notes to the reader of that file and
    neither belongs on a résumé he sends.

    `date_to_emphasised` is TRUE on exactly one role. Migration 012 records why:
    CLAUDE.md, master/README.md and the export checklist all insist VoltusWave
    must read Apr 2026, "and the bold is the file shouting it. A plain-text store
    drops it silently and it does not surface until an exported PDF."
    """
    runs = [(section["company"], True), (" · " + section["role_title"], False),
            (" · " + section["date_from"] + " – ", False)]
    runs.append((section["date_to"], bool(section["date_to_emphasised"])))
    if section["location"]:
        runs.append((" · " + section["location"], False))
    return runs


def build(model: dict) -> Document:
    document = Document()
    _style_document(document)

    document.add_paragraph(CANDIDATE_NAME, style="Heading 1")

    line = document.add_paragraph(style="Normal")
    for text, bold, url in contact(model["profile"]):
        if url:
            _add_hyperlink(line, url, text, bold)
        else:
            run = line.add_run(text)
            # ⛔ Set bold ONLY when true. `run.bold = False` writes an explicit
            # <w:b w:val="0"/>, and direct formatting outranks the style — 299 of
            # them meant that editing "List Bullet" in Word's style pane did
            # NOTHING. Leaving it None inherits the style, which is what makes
            # the document editable.
            if bold:
                run.bold = True

    by_id = {s["section_id"]: s for s in model["sections"]}

    # Headline — the only block with no bold, legitimately: the DB's own
    # `resume_blocks_bold` constraint is scoped to experience sections. Do not
    # assert bold here and never invent it.
    headline = document.add_paragraph(style="Normal")
    _add_runs(headline, inline_runs(by_id["quick-headline"]["blocks"][0]["html"]))
    headline.paragraph_format.space_after = Pt(6)

    document.add_paragraph("Summary", style="Heading 2")
    summary = document.add_paragraph(style="Normal")
    _add_runs(summary, inline_runs(by_id["quick-summary"]["blocks"][0]["html"]))

    document.add_paragraph("Key Skills", style="Heading 2")
    for section in model["sections"]:
        if section["kind"] != "skills":
            continue
        document.add_paragraph(RE_SKILLS_PREFIX.sub("", section["heading"]),
                               style="Heading 3")
        for block in section["blocks"]:
            _add_runs(document.add_paragraph(style="List Bullet"),
                      inline_runs(block["html"]))

    document.add_paragraph("Experience", style="Heading 2")
    for section in model["sections"]:
        if section["kind"] != "experience":
            continue
        _add_runs(document.add_paragraph(style="Heading 3"), _role_heading(section))
        for block in section["blocks"]:
            _add_runs(document.add_paragraph(style="List Bullet"),
                      inline_runs(block["html"]))

    document.add_paragraph("Education", style="Heading 2")
    for row in model["education"]:
        para = document.add_paragraph(style="Normal")
        _add_runs(para, [(row["credential"], True),
                         (", " + row["institution"] + " (" + row["date_range"] + ")", False)])

    # ⛔ `resume_certifications` is DELIBERATELY EMPTY — migration 012: "His
    # certifications live only in the Hiration card … The emptiness is the record
    # of that boundary", and "inventing rows to make 'the database is the source'
    # sound complete is the shape of the bug migration 007 paid for on
    # source_url." So the heading is emitted only if there is something under it.
    # The one certification-shaped item in the corpus, the IIIT PG Diploma, is
    # stored as education and renders above, which is where the master puts it.
    if model["certifications"]:
        document.add_paragraph("Certifications", style="Heading 2")
        for row in model["certifications"]:
            para = document.add_paragraph(style="Normal")
            runs = [(row["name"], True)]
            if row["issuer"]:
                runs.append((", " + row["issuer"], False))
            if row["awarded"]:
                runs.append((" (" + row["awarded"] + ")", False))
            _add_runs(para, runs)

    return document


# ---------------------------------------------------------------------------
# check — THE GATE, run against a Document object whatever its provenance
# ---------------------------------------------------------------------------

def _paragraphs(document: Document) -> list[dict]:
    out = []
    for para in document.paragraphs:
        # ⛔ NOT para.runs. python-docx returns only DIRECT-CHILD <w:r>, so every
        # run nested inside a <w:hyperlink> is invisible — the bolded LinkedIn
        # slug among them. That is why the report printed 223 bold spans one line
        # above 224 <w:b/> elements: a reporting artefact that also left bold
        # inside any hyperlink UNGATED. Walk the XML instead, in document order.
        runs = []
        for r in para._p.findall(
                ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"):
            texts = r.findall(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
            text = "".join(t.text or "" for t in texts)
            rpr = r.find(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
            bold = False
            if rpr is not None:
                b = rpr.find(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b")
                bold = b is not None and b.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") != "0"
            runs.append((text, bold))
        out.append({"style": para.style.name, "text": para.text, "runs": runs})
    return out


def _bold_spans(runs: list[tuple[str, bool]]) -> list[str]:
    """Contiguous bold runs, joined — what a reader sees as one bolded fact."""
    spans, current = [], []
    for text, bold in runs:
        if bold:
            current.append(text)
        elif current:
            spans.append("".join(current))
            current = []
    if current:
        spans.append("".join(current))
    return spans


def check(document: Document, model: dict) -> list[str]:
    """Every failure, listed. Returns [] when the document is right.

    Never returns early: a report naming one problem when there are four is how
    a second run finds a "new" defect that was there all along.
    """
    problems: list[str] = []
    paras = _paragraphs(document)
    by_style: dict[str, list[dict]] = {}
    for para in paras:
        by_style.setdefault(para["style"], []).append(para)
    bullets = by_style.get("List Bullet", [])

    # 1. Every live block present, text byte-identical to the DB's plain column.
    expected = [b for s in model["sections"] if s["kind"] in ("skills", "experience")
                for b in s["blocks"]]
    got = [p["text"] for p in bullets]
    if len(got) != len(expected):
        problems.append(f"bullet count {len(got)} != {len(expected)} live skills+experience blocks")
    for block, text in zip(expected, got):
        if text != block["text"]:
            problems.append(f"bullet {block['key']} text differs\n"
                            f"      db   : {block['text']!r}\n"
                            f"      docx : {text!r}")

    # 2. Headline and summary, likewise — they are Normal paragraphs, not bullets.
    for section_id in ("quick-headline", "quick-summary"):
        block = next(s for s in model["sections"] if s["section_id"] == section_id)["blocks"][0]
        if block["text"] not in [p["text"] for p in paras]:
            problems.append(f"{section_id} paragraph missing or altered")

    # 3. BOLD — the pass/fail condition. Every <strong> span in the database
    #    becomes a bold span in the document, in order.
    db_spans = [span for s in model["sections"] for b in s["blocks"]
                for span in strong_spans(b["html"])]
    doc_spans = [span for p in paras for span in _bold_spans(p["runs"])]
    # ⛔ MULTIPLICITY, not membership. `s not in doc_spans` asks only whether the
    # text appears bold SOMEWHERE. Of 209 database spans just 182 are distinct —
    # "Java and Spring Boot" occurs four times — so bold could vanish from three
    # of those four and a membership test would still pass. 27 occurrences were
    # invisible to the gate. resume-issues-to-avoid/ rule 9 is precisely this
    # failure (bold silently stripped on export, every bullet then flagged "no
    # bolded fact"), so the one detector for it must not be blind to repeats.
    from collections import Counter
    want, have = Counter(db_spans), Counter(doc_spans)
    short = {k: want[k] - have.get(k, 0) for k in want if want[k] > have.get(k, 0)}
    if short:
        total = sum(short.values())
        problems.append(f"{total} of {len(db_spans)} database <strong> occurrence(s) "
                        f"are NOT bold in the .docx: "
                        f"{[(k, f'want {want[k]}, have {have.get(k, 0)}') for k in list(short)[:5]]}")

    # 4. All fifteen sections reachable, all ten roles headed with their dates.
    heads = [p["text"] for p in by_style.get("Heading 3", [])]
    for section in model["sections"]:
        if section["kind"] == "skills":
            name = RE_SKILLS_PREFIX.sub("", section["heading"])
            if name not in heads:
                problems.append(f"skills group heading missing: {name!r}")
        elif section["kind"] == "experience":
            wanted = "".join(t for t, _ in _role_heading(section))
            if wanted not in heads:
                problems.append(f"role heading missing: {wanted!r}")
    for label in ("Summary", "Key Skills", "Experience", "Education"):
        if label not in [p["text"] for p in by_style.get("Heading 2", [])]:
            problems.append(f"section heading missing: {label!r}")
    if model["certifications"] and "Certifications" not in [
            p["text"] for p in by_style.get("Heading 2", [])]:
        problems.append("certifications exist in the DB but no Certifications heading")

    # 5. Education, contact, name.
    for row in model["education"]:
        if not any(row["credential"] in p["text"] and row["institution"] in p["text"]
                   for p in paras):
            problems.append(f"education row missing: {row['credential']!r}")
    wanted_contact = "".join(t for t, _, _ in contact(model["profile"]))
    if not any(p["text"] == wanted_contact for p in paras):
        problems.append(f"contact line missing or altered — wanted {wanted_contact!r}")
    if not any(p["text"] == CANDIDATE_NAME for p in by_style.get("Heading 1", [])):
        problems.append("name heading missing")

    # 6. ATS layout — the parsing failure `resume-issues-to-avoid/` names.
    body = document.element.body
    if body.findall(".//" + qn("w:tbl")):
        problems.append("document contains a table — ATS parsers mis-read multi-column layout")
    if body.findall(".//" + qn("w:txbxContent")):
        problems.append("document contains a text box")
    for para in paras:
        if "•" in para["text"]:
            problems.append(f"literal bullet glyph in text: {para['text'][:60]!r}")

    return problems


def _report(document: Document, model: dict) -> None:
    paras = _paragraphs(document)
    db_spans = [span for s in model["sections"] for b in s["blocks"]
                for span in strong_spans(b["html"])]
    doc_spans = [span for p in paras for span in _bold_spans(p["runs"])]
    xml = document.element.body.xml
    print(f"  blocks in DB      : {sum(len(s['blocks']) for s in model['sections'])}")
    print(f"  paragraphs        : {len(paras)}")
    print(f"  bullets           : {sum(1 for p in paras if p['style'] == 'List Bullet')}")
    print(f"  role headings     : {sum(1 for p in paras if p['style'] == 'Heading 3')}")
    print(f"  DB <strong> spans : {len(db_spans)}")
    print(f"  bold spans in docx: {len(doc_spans)}")
    print(f"  <w:b/> elements   : {len(re.findall(r'<w:b/>', xml))}")
    print(f"  xml:space=preserve: {len(re.findall(r'xml:space=\"preserve\"', xml))}")
    print(f"  tables · textboxes: {len(re.findall(qn('w:tbl'), xml))} · "
          f"{len(re.findall(qn('w:txbxContent'), xml))}")


# ---------------------------------------------------------------------------

def generate(out_path: Path) -> int:
    model = fetch()
    document = build(model)

    # ⛔ CHECKED BEFORE IT IS WRITTEN. A silently-wrong résumé on disk is worse
    # than no résumé: he opens it, it looks finished, and the defect surfaces in
    # a recruiter's ATS. Same refusal posture as `resume_db.generate`.
    # ⛔ The stock python-docx template ships docProps that say
    # <dc:creator>python-docx</dc:creator>, an empty <dc:title/> and
    # dcterms:created 2013-12-23. All visible in Word's Info pane and in macOS
    # Get Info, and some applicant tracking systems ingest dc:title as the
    # document's name. On a file he uploads to job boards that is a template
    # watermark. Stamp it with his own details instead.
    core = document.core_properties
    core.author = core.last_modified_by = "Abhisheik Deo"
    core.title = "Abhisheik Deo — Resume"
    core.subject = "Principal Software Architect"
    core.comments = ""
    core.category = core.keywords = ""

    problems = check(document, model)
    if problems:
        print(f"[resume-docx] REFUSING to write {out_path} — "
              f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"    ⛔ {problem}", file=sys.stderr)
        return 1

    # ⛔ NEVER over the round-trip verification artefact. `resume_db.py` guards the
    # same file the same way; without this, `--out master/upgrad_resume.html`
    # replaces the one artefact that proves a parse did not drop a <strong> —
    # with a binary zip.
    protected = (ROOT / "master" / "upgrad_resume.html").resolve()
    if out_path.resolve() == protected:
        raise SystemExit(f"[resume-docx] REFUSING: {out_path} is the round-trip "
                         f"verification artefact, not an output path")
    if out_path.suffix.lower() != ".docx":
        raise SystemExit(f"[resume-docx] REFUSING: {out_path} is not a .docx path")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic: a crash mid-save must not leave a truncated .docx that Word opens
    # as corrupt. Same pattern as resume_db.generate.
    import tempfile
    with tempfile.NamedTemporaryFile(dir=str(out_path.parent), suffix=".docx",
                                     delete=False) as tmp:
        tmp_path = pathlib.Path(tmp.name)
    document.save(str(tmp_path))
    tmp_path.replace(out_path)
    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"[resume-docx] wrote {out_path} "
          f"({out_path.stat().st_size:,} bytes, sha256 {digest[:8]}…)")
    _report(document, model)
    return 0


def verify(out_path: Path) -> int:
    if not out_path.exists():
        print(f"[resume-docx] no file at {out_path} — run `generate` first", file=sys.stderr)
        return 2
    model = fetch()
    document = Document(str(out_path))   # re-read from disk, not the object in memory
    print(f"{'=' * 68}\n  DOCX GATE — {out_path}\n{'=' * 68}")
    print(f"  sha256            : {hashlib.sha256(out_path.read_bytes()).hexdigest()}")
    _report(document, model)
    problems = check(document, model)
    if problems:
        print(f"\n  ⛔ {len(problems)} problem(s):")
        for problem in problems:
            print(f"    - {problem}")
        return 1
    print("\n  ✅ Every live block present and byte-identical to the database, "
          "every <strong> span bold, every section and role heading present.")
    if not model["certifications"]:
        print("  ⚠ resume_certifications holds 0 rows — deliberately (migration 012). "
              "No Certifications section is emitted, and none is invented.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="The master résumé as a Word document, rendered from jobs_tracker_v2.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_gen = sub.add_parser("generate", help="render the DB to a .docx")
    p_gen.add_argument("--out", type=Path, default=OUT, help=f"output path (default {OUT})")
    p_ver = sub.add_parser("verify", help="re-open the .docx and prove it from the DB")
    p_ver.add_argument("--out", type=Path, default=OUT, help=f"file to check (default {OUT})")

    args = parser.parse_args()
    try:
        return generate(args.out) if args.cmd == "generate" else verify(args.out)
    except BuildError as exc:
        print(f"[resume-docx] REFUSING: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
