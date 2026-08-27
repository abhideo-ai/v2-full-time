#!/usr/bin/env python3
"""The master résumé, stored in and rendered from `jobs_tracker_v2`.

    JOBS_TRACKER_DSN=dbname=jobs_tracker_v2   (default)

⚑ THE DIRECTION IS FLIPPED HERE, AND ONLY FOR THE MASTER. His words, 2026-08-27:
"remember, you SHOULD be using a DB to store the information", "AND prepare the
HTML from that DB", "starting now, we do that", "from the master resume".

    resume_documents + resume_roles + resume_education + resume_profile
    + resume_sections + resume_blocks                          ← AUTHORED
                |
                v   resume_db.py generate
       master/upgrad_resume.html                                ← BUILD ARTEFACT
                |
                +--> upgrad_apply.py -> Hiration -> the PDF he reviews
                +--> jobs_sync.py --bullets -> resume_bullets    ← STILL DERIVED

Nothing in the exporter changes. `upgrad_apply.py` parses `upgrad_resume.html`
by section id; whether that file was typed or generated is invisible to it. The
six per-seat workspaces are untouched and their files are still hand-authored.

    resume_db.py load                 parse master/upgrad_resume.html into the DB
    resume_db.py generate [--out P]   render the DB back to HTML
    resume_db.py verify               load, generate, and diff against the file

⛔ WHY THE PARSE IS A VERBATIM SUBSTRING AND NOT BEAUTIFULSOUP.
`upgrad_resume_paste._inner_html()` is lossless in SUBSTANCE and not in spelling,
because bs4 applies two different escape rules inside one paragraph: `str()` on a
text node re-escapes nothing, while `str()` on a Tag re-escapes & < > . So

    <p>A &amp; B</p>                  comes back  "A & B"          (lossy)
    <p><strong>A &amp; B</strong></p> comes back  "<strong>A &amp; B</strong>"
    <p>P99 &lt;strong&gt;fast&lt;/strong&gt;</p>
                                      comes back  a REAL <strong> tag

That last one is the landmine: escaped text becomes markup in one pass and is
stable thereafter, so a second round-trip check cannot see it. No bullet contains
`&lt;` today — but CLAUDE.md's own open-claim list carries the phrase
"warm-path P99 < 200 ms". This module never parses a bullet body at all. It takes
the bytes between `<p>` and `</p>` and stores them, and it REFUSES a file whose
skeleton is not exactly the shape it expects rather than guessing.

Sibling of `jobs_db.py` / `jobs_sync.py`: same connection pattern, raw SQL, dict
rows, no ORM. Jinja2 renders and does nothing else.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import html as html_mod
import os
import re
import sys
import tempfile
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("JOBS_TRACKER_DSN", "dbname=jobs_tracker_v2")
ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "master" / "upgrad_resume.html"
GENERATED = ROOT / "master" / "upgrad_resume.generated.html"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
DOC_KEY = "master"

# ⛔ The ten ids `upgrad_apply.py` parses. master/README.md records the trap: a
# misspelt id is SKIPPED SILENTLY and the export still looks successful. Nothing
# is written unless all ten are present and non-empty.
CONTRACT_IDS = [
    "quick-headline", "quick-summary",
    "quick-skills-tls", "quick-skills-ee", "quick-skills-bd",
    "quick-vp", "quick-deque", "quick-rocket",
    "quick-voltuswave-cofounder", "quick-teletext",
]

# Section id -> kind. Shared vocabulary with upgrad_resume_paste.SECTION_ORDER;
# imported rather than restated so the two cannot drift.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upgrad_resume_paste import SECTION_ORDER  # noqa: E402

KIND_FOR = dict(SECTION_ORDER)


# ---------------------------------------------------------------------------
# Parsing — strict, line-oriented, verbatim
# ---------------------------------------------------------------------------
# Every pattern below is anchored to the WHOLE line. A file that does not match
# is a file this module refuses, loudly, rather than one it half-understands.

RE_DIV      = re.compile(r'^<div class="section copy-target" id="([a-z0-9_-]+)">$')
RE_H2       = re.compile(r'^<h2>(.*)</h2>$')
RE_BTN      = re.compile(r'^  <button class="copy-btn" data-copy-target="#([a-z0-9_-]+)"'
                         r' data-copy-html="1">Copy</button>$')
RE_P        = re.compile(r'^  <p>(.*)</p>$')
RE_HEAD_NUM = re.compile(r'^(\d+)\. (.*)$')

# The named entities the master uses. `resume_plain()` in migration 012 knows
# exactly these. Anything else would survive into `text` unexpanded, so it is a
# hard failure here rather than a surprise in a word count six weeks later.
KNOWN_ENTITIES = {"amp", "lt", "gt", "mdash", "ndash", "nbsp", "quot", "apos"}
RE_ENTITY = re.compile(r"&([A-Za-z][A-Za-z0-9]*);")


class ParseError(RuntimeError):
    """The file is not the shape this module knows. Never guessed around."""


def _esc(value: str) -> str:
    """Escape & < > and nothing else — the template's `h` filter.

    quote=False on purpose: McDonald's must keep its apostrophe, and the file
    never escapes quotes inside text.
    """
    return html_mod.escape(value, quote=False)


def _cell_text(cell_html: str) -> str:
    """A table cell's plain value, asserting the escape round-trips exactly.

    Anything whose re-escaped form differs from the source — a `&mdash;`, a
    stray tag — raises rather than being silently normalised into a different
    file on the way back out.
    """
    plain = html_mod.unescape(cell_html)
    if _esc(plain) != cell_html:
        raise ParseError(
            f"table cell does not survive escape/unescape verbatim: {cell_html!r} "
            f"-> {plain!r} -> {_esc(plain)!r}"
        )
    return plain


def _split_row(line: str, tag: str, n: int) -> list[str]:
    m = re.fullmatch(rf"<tr><{tag}>(.*)</{tag}></tr>", line)
    if not m:
        raise ParseError(f"not a <{tag}> row: {line!r}")
    cells = m.group(1).split(f"</{tag}><{tag}>")
    if len(cells) != n:
        raise ParseError(f"expected {n} cells, found {len(cells)}: {line!r}")
    return cells


def parse_master(source: str) -> dict:
    """Every storable thing in the master, verbatim. Touches no database."""
    for ent in RE_ENTITY.findall(source):
        if ent not in KNOWN_ENTITIES:
            raise ParseError(
                f"unknown named entity &{ent}; — resume_plain() in migration 012 "
                f"would leave it unexpanded in `text`. Add it there first."
            )

    lines = source.split("\n")
    if lines[-1] != "":
        raise ParseError("file does not end with exactly one newline")

    div_at = [i for i, ln in enumerate(lines) if RE_DIV.match(ln)]
    if not div_at:
        raise ParseError("no `<div class=\"section copy-target\" id=…>` found")

    # ---- the fifteen sections -------------------------------------------
    sections, prev_end = [], None
    for i in div_at:
        sec_id = RE_DIV.match(lines[i]).group(1)
        h2 = RE_H2.match(lines[i - 1])
        if not h2:
            raise ParseError(f"{sec_id}: the <h2> must be the line before its div, "
                             f"got {lines[i - 1]!r}")
        if prev_end is not None and lines[prev_end + 1:i - 1] != [""]:
            raise ParseError(f"{sec_id}: expected exactly one blank line before its "
                             f"<h2>, got {lines[prev_end + 1:i - 1]!r}")
        btn = RE_BTN.match(lines[i + 1])
        if not btn or btn.group(1) != sec_id:
            raise ParseError(f"{sec_id}: the copy button must be the first line of "
                             f"the div and target its own id, got {lines[i + 1]!r}")
        blocks, j = [], i + 2
        while j < len(lines) and lines[j] != "</div>":
            p = RE_P.match(lines[j])
            if not p:
                raise ParseError(
                    f"{sec_id}: every bullet must be one line of exactly "
                    f"'  <p>…</p>', got {lines[j]!r}")
            blocks.append(p.group(1))
            j += 1
        if j >= len(lines):
            raise ParseError(f"{sec_id}: unterminated section div")
        if not blocks:
            raise ParseError(f"{sec_id}: no bullets")
        num = RE_HEAD_NUM.match(h2.group(1))
        if not num:
            raise ParseError(f"{sec_id}: <h2> must start 'N. ', got {h2.group(1)!r}")
        if sec_id not in KIND_FOR:
            raise ParseError(f"{sec_id}: not in upgrad_resume_paste.SECTION_ORDER")
        sections.append({
            "ord":          int(num.group(1)),
            "section_id":   sec_id,
            "section_kind": KIND_FOR[sec_id],
            "heading_html": num.group(2),
            "card_only":    sec_id.startswith("p-"),
            "blocks":       blocks,
        })
        prev_end = j

    order = [s["section_id"] for s in sections]
    if order != [sid for sid, _ in SECTION_ORDER]:
        raise ParseError(f"section order/inventory differs from SECTION_ORDER: {order}")
    if [s["ord"] for s in sections] != list(range(1, len(sections) + 1)):
        raise ParseError("<h2> numbering is not 1..N in file order")

    # ---- prologue --------------------------------------------------------
    head = lines[:div_at[0] - 1]
    tail = lines[prev_end + 1:]

    def expect(idx: int, literal: str) -> None:
        if head[idx] != literal:
            raise ParseError(f"line {idx + 1}: expected {literal!r}, got {head[idx]!r}")

    expect(0, "<!doctype html>")
    expect(2, "<head>")
    expect(3, '  <meta charset="utf-8" />')
    expect(4, '  <meta name="viewport" content="width=device-width, initial-scale=1" />')
    expect(8, "</head>")
    expect(9, "<body>")
    expect(10, '<main class="page" id="main">')
    expect(11, "")

    def one(idx: int, pattern: str, what: str) -> str:
        m = re.fullmatch(pattern, head[idx])
        if not m:
            raise ParseError(f"line {idx + 1}: cannot read {what} from {head[idx]!r}")
        return m.group(1)

    doc = {
        "doc_key":         DOC_KEY,
        "lang":            one(1, r'<html lang="([^"]+)">', "lang"),
        "title":           _cell_text(one(5, r"  <title>(.*)</title>", "title")),
        "favicon_href":    one(6, r'  <link rel="icon" type="image/svg\+xml" href="([^"]+)" />',
                               "favicon"),
        "stylesheet_href": one(7, r'  <link rel="stylesheet" href="([^"]+)" />', "stylesheet"),
    }

    # the parser-contract comment block
    if not head[12].startswith("<!--"):
        raise ParseError("expected the parser-contract comment at line 13")
    close = next(k for k in range(12, len(head)) if head[k].endswith("-->"))
    comment = "\n".join(head[12:close + 1])
    doc["contract_comment"] = comment[len("<!--"):-len("-->")]
    if head[close + 1] != "":
        raise ParseError("expected a blank line after the contract comment")

    k = close + 2
    h1 = re.fullmatch(r"<h1>(.*)</h1>", head[k])
    if not h1:
        raise ParseError(f"expected <h1> at line {k + 1}, got {head[k]!r}")
    if _cell_text(h1.group(1)) != doc["title"]:
        raise ParseError("<h1> and <title> disagree; the template renders one value")

    k += 1
    intro_start = k
    while not head[k].endswith("</p>"):
        k += 1
    intro = "\n".join(head[intro_start:k + 1])
    doc["intro_html"] = intro[len("<p>"):-len("</p>")]
    k += 1
    if head[k] != "":
        raise ParseError("expected a blank line after the intro paragraph")

    # ---- the dates table -> resume_roles ---------------------------------
    k += 1
    doc["dates_heading"] = _cell_text(one_h2(head, k, "the dates heading"))
    k += 1
    if head[k] != "<table>":
        raise ParseError(f"expected <table> at line {k + 1}")
    k += 1
    if _split_row(head[k], "th", 6) != ["#", "Employer", "Title", "From", "To", "Location"]:
        raise ParseError("the dates table header row is not the expected six columns")
    k += 1
    roles = []
    while head[k] != "</table>":
        cells = _split_row(head[k], "td", 6)
        emph = re.fullmatch(r"<strong>(.*)</strong>", cells[4])
        date_to_html = emph.group(1) if emph else cells[4]
        for label, raw in (("company", cells[1]), ("title", cells[2]),
                           ("from", cells[3]), ("to", date_to_html),
                           ("location", cells[5])):
            if "<" in raw:
                raise ParseError(
                    f"role row {cells[0]}: unexpected markup in the {label} cell "
                    f"({raw!r}). The only emphasis this template knows how to "
                    f"reproduce is <strong> on the end date. Refusing to drop it.")
        roles.append({
            "n":                  int(cells[0]),
            "company":            _cell_text(cells[1]),
            "role_title":         _cell_text(cells[2]),
            "date_from":          _cell_text(cells[3]),
            "date_to":            _cell_text(date_to_html),
            "location":           _cell_text(cells[5]),
            "date_to_emphasised": bool(emph),
        })
        k += 1
    if [r["n"] for r in roles] != list(range(1, len(roles) + 1)):
        raise ParseError("the dates table is not numbered 1..N in order")

    # ---- education -------------------------------------------------------
    k += 1
    edu_start = k
    while not head[k].endswith("</p>"):
        k += 1
    edu = "\n".join(head[edu_start:k + 1])
    m = re.fullmatch(r"<p><strong>([^<]+):</strong> (.*)</p>", edu, re.S)
    if not m:
        raise ParseError("the education paragraph is not '<p><strong>Label:</strong> …</p>'")
    doc["education_label"] = _cell_text(m.group(1))
    edu_lines = m.group(2).split("\n")
    # The last line is the reader-facing instruction ("Never downgrade the MS."),
    # not résumé content. It is the only line that is markup rather than a
    # `credential, institution (dates).` sentence.
    note = edu_lines[-1] if edu_lines[-1].startswith("<strong>") else None
    entries = edu_lines[:-1] if note else edu_lines
    doc["education_note_html"] = note
    education = []
    for i, line in enumerate(entries, 1):
        em = re.fullmatch(r"(.*?), ([^,]+) \(([^()]*)\)\.", line)
        if not em:
            raise ParseError(
                f"education line {i} is not 'credential, institution (dates).': {line!r}")
        education.append({
            "ord":         i,
            "credential":  _cell_text(em.group(1)),
            "institution": _cell_text(em.group(2)),
            "date_range":  _cell_text(em.group(3)),
            # CLAUDE.md: "Education = MS in Computer Science, University of
            # Houston. Never downgrade it." The first entry is the highest degree
            # and the schema allows exactly one.
            "is_highest":  i == 1,
        })
    k += 1
    if head[k] != "":
        raise ParseError("expected a blank line after the education paragraph")

    # ---- personal information -------------------------------------------
    k += 1
    doc["personal_heading"] = _cell_text(one_h2(head, k, "the personal-information heading"))
    k += 1
    pi_start = k
    while not head[k].endswith("</p>"):
        k += 1
    pi = "\n".join(head[pi_start:k + 1])
    doc["personal_note_html"] = pi[len("<p>"):-len("</p>")]
    k += 1
    if head[k] != "<table>":
        raise ParseError(f"expected <table> at line {k + 1}")
    k += 1
    if _split_row(head[k], "th", 2) != ["Field", "Value"]:
        raise ParseError("the personal-information header row is not Field | Value")
    k += 1
    profile = []
    while head[k] != "</table>":
        cells = _split_row(head[k], "td", 2)
        profile.append({"ord": len(profile) + 1,
                        "field_label": _cell_text(cells[0]),
                        "value_html": cells[1]})
        k += 1
    k += 1
    if head[k:] != [""]:
        raise ParseError(f"unexpected content between the personal table and the "
                         f"first section: {head[k:]!r}")

    # ---- epilogue --------------------------------------------------------
    if tail[0] != "" or tail[1] != "</main>":
        raise ParseError(f"expected a blank line then </main>, got {tail[:2]!r}")
    script = re.fullmatch(r'<script src="([^"]+)" defer></script>', tail[2])
    if not script:
        raise ParseError(f"cannot read the copy.js path from {tail[2]!r}")
    doc["script_src"] = script.group(1)
    if tail[3:] != ["</body>", "</html>", ""]:
        raise ParseError(f"unexpected tail: {tail[3:]!r}")

    return {"doc": doc, "roles": roles, "education": education,
            "profile": profile, "sections": sections}


def one_h2(lines: list[str], idx: int, what: str) -> str:
    m = RE_H2.match(lines[idx])
    if not m:
        raise ParseError(f"line {idx + 1}: cannot read {what} from {lines[idx]!r}")
    return m.group(1)


# ---------------------------------------------------------------------------
# bullet_key — stable identity, NOT position
# ---------------------------------------------------------------------------
# DESIGN-bullets.md §2: "`ord` must not be the key: re-ordering the master would
# silently re-point every seat's selection at a different bullet."
#
# A key is derived once, from the bullet's own leading words, and then CARRIED
# FORWARD across reloads for any bullet whose html is unchanged — so re-running
# `load` after editing one bullet does not renumber the other ninety.

def _slug(text: str, words: int = 4) -> str:
    toks = re.findall(r"[A-Za-z0-9]+", text.lower())[:words]
    return "-".join(toks) or "bullet"


def derive_keys(sections: list[dict], carried: dict[str, str]) -> None:
    """Fill in each block's bullet_key in place. `carried` maps html -> old key."""
    used: set[str] = set()
    for sec in sections:
        sec["keys"] = []
        for raw in sec["blocks"]:
            old = carried.get(raw)
            if old and old not in used:
                used.add(old)
                sec["keys"].append(old)
            else:
                sec["keys"].append(None)
    for sec in sections:
        prefix = sec["section_id"].split("-", 1)[1]
        for i, raw in enumerate(sec["blocks"]):
            if sec["keys"][i] is not None:
                continue
            base = f"{prefix}-{_slug(html_mod.unescape(re.sub('<[^>]+>', '', raw)))}"
            key, n = base, 1
            while key in used:
                n += 1
                key = f"{base}-{n}"
            used.add(key)
            sec["keys"][i] = key


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------

def load_from(path: Path, source: str | None = None, quiet: bool = False) -> dict:
    """Parse one master résumé into the database. Idempotent, one transaction."""
    raw = source if source is not None else path.read_text(encoding="utf-8")
    parsed = parse_master(raw)

    missing = [s for s in CONTRACT_IDS
               if s not in {sec["section_id"] for sec in parsed["sections"]}]
    if missing:
        raise ParseError(f"parser-contract ids absent: {missing}")

    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT html, bullet_key FROM resume_blocks WHERE doc_key = %s",
                        (DOC_KEY,))
            carried = {r["html"]: r["bullet_key"] for r in cur.fetchall()}
            derive_keys(parsed["sections"], carried)

            # ⛔ RETIRED BULLETS SURVIVE A RELOAD.
            # `retired_at` exists so a bullet leaves the master by being retired,
            # never deleted — "a sent seat may still reference it, and history must
            # stay readable" (db/DESIGN-bullets.md §2). But render() filters
            # retired rows out, so they are absent from the generated HTML, and the
            # DELETE below cascades them away. Reloading then lost them silently —
            # the feature quietly destroying the thing it was built to preserve.
            # Proven by mutation on 2026-08-27. Carry them across, exactly as
            # bullet_key is carried.
            cur.execute("""SELECT section_id, ord, html, bullet_key, retired_at
                             FROM resume_blocks
                            WHERE doc_key = %s AND retired_at IS NOT NULL""", (DOC_KEY,))
            retired = cur.fetchall()

            # Delete-and-reinsert wholesale, exactly like `jobs_sync --bullets`,
            # so a half-written document can never be committed. resume_documents
            # cascades to every child table.
            cur.execute("DELETE FROM resume_documents WHERE doc_key = %s", (DOC_KEY,))
            d = parsed["doc"]
            cur.execute("""
                INSERT INTO resume_documents (
                    doc_key, title, lang, stylesheet_href, favicon_href, script_src,
                    contract_comment, intro_html, dates_heading, education_label,
                    education_note_html, personal_heading, personal_note_html)
                VALUES (%(doc_key)s, %(title)s, %(lang)s, %(stylesheet_href)s,
                        %(favicon_href)s, %(script_src)s, %(contract_comment)s,
                        %(intro_html)s, %(dates_heading)s, %(education_label)s,
                        %(education_note_html)s, %(personal_heading)s,
                        %(personal_note_html)s)""", d)

            for r in parsed["roles"]:
                cur.execute("""
                    INSERT INTO resume_roles (doc_key, n, company, role_title,
                        date_from, date_to, location, date_to_emphasised)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (DOC_KEY, r["n"], r["company"], r["role_title"], r["date_from"],
                     r["date_to"], r["location"], r["date_to_emphasised"]))

            for e in parsed["education"]:
                cur.execute("""
                    INSERT INTO resume_education (doc_key, ord, credential,
                        institution, date_range, is_highest)
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    (DOC_KEY, e["ord"], e["credential"], e["institution"],
                     e["date_range"], e["is_highest"]))

            for p in parsed["profile"]:
                cur.execute("""
                    INSERT INTO resume_profile (doc_key, ord, field_label, value_html)
                    VALUES (%s,%s,%s,%s)""",
                    (DOC_KEY, p["ord"], p["field_label"], p["value_html"]))

            seen_experience = 0
            for sec in parsed["sections"]:
                role_n = None
                if sec["section_kind"] == "experience":
                    seen_experience += 1
                    role_n = seen_experience
                cur.execute("""
                    INSERT INTO resume_sections (doc_key, ord, section_id,
                        section_kind, heading_html, card_only, role_n)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (DOC_KEY, sec["ord"], sec["section_id"], sec["section_kind"],
                     sec["heading_html"], sec["card_only"], role_n))
                for i, raw in enumerate(sec["blocks"], 1):
                    cur.execute("""
                        INSERT INTO resume_blocks (doc_key, section_id, section_kind,
                            ord, bullet_key, html)
                        VALUES (%s,%s,%s,%s,%s,%s)""",
                        (DOC_KEY, sec["section_id"], sec["section_kind"], i,
                         sec["keys"][i - 1], raw))

            # Put the retired bullets back. They are invisible to render(), so
            # they cannot affect the round trip — they exist so a sent seat that
            # still references one can be read later. Appended past the live
            # ords so they never collide with a live bullet's position.
            # A retired bullet whose text is BACK in the file is no longer retired —
            # the live row supersedes it, and re-inserting both would violate
            # UNIQUE (doc_key, bullet_key). Carry only the ones the file no longer
            # contains; those are the ones history would otherwise lose.
            cur.execute("SELECT bullet_key FROM resume_blocks WHERE doc_key=%s", (DOC_KEY,))
            live_keys = {r["bullet_key"] for r in cur.fetchall()}
            revived = [r for r in retired if r["bullet_key"] in live_keys]
            retired = [r for r in retired if r["bullet_key"] not in live_keys]
            if revived and not quiet:
                print(f"[resume-db] {len(revived)} retired bullet(s) are back in the file "
                      f"— treating them as live again, not duplicating them")

            if retired and not quiet:
                print(f"[resume-db] carrying {len(retired)} retired bullet(s) across the reload")

            tail: dict[str, int] = {}
            for r in retired:
                sid = r["section_id"]
                if sid not in tail:
                    cur.execute("""SELECT coalesce(max(ord), 0) AS m FROM resume_blocks
                                    WHERE doc_key=%s AND section_id=%s""", (DOC_KEY, sid))
                    tail[sid] = cur.fetchone()["m"]
                tail[sid] += 1
                cur.execute("""
                    INSERT INTO resume_blocks (doc_key, section_id, section_kind,
                        ord, bullet_key, html, retired_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (DOC_KEY, sid,
                     next((x["section_kind"] for x in parsed["sections"]
                           if x["section_id"] == sid), "experience"),
                     tail[sid], r["bullet_key"], r["html"], r["retired_at"]))
        conn.commit()

    n_blocks = sum(len(s["blocks"]) for s in parsed["sections"])
    if not quiet:
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        print(f"[resume-db] loaded {DOC_KEY} from {path} (sha256 {digest[:8]}…)")
        print(f"[resume-db]   {len(parsed['sections'])} sections · {n_blocks} blocks · "
              f"{len(parsed['roles'])} roles · {len(parsed['education'])} education · "
              f"{len(parsed['profile'])} profile fields")
    return {"sections": len(parsed["sections"]), "blocks": n_blocks,
            "roles": len(parsed["roles"])}


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

def _env():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        # ⛔ All four are load-bearing — see the template's own header.
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        newline_sequence="\n",
    )
    env.filters["h"] = _esc
    return env


def render() -> str:
    with psycopg.connect(DSN, row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM resume_documents WHERE doc_key = %s", (DOC_KEY,))
        doc = cur.fetchone()
        if doc is None:
            raise SystemExit(f"[resume-db] no document {DOC_KEY!r} — run `resume_db.py load`")
        cur.execute("SELECT * FROM resume_roles WHERE doc_key=%s ORDER BY n", (DOC_KEY,))
        roles = cur.fetchall()
        cur.execute("SELECT * FROM resume_education WHERE doc_key=%s ORDER BY ord", (DOC_KEY,))
        education = cur.fetchall()
        cur.execute("SELECT * FROM resume_profile WHERE doc_key=%s ORDER BY ord", (DOC_KEY,))
        profile = cur.fetchall()
        cur.execute("""SELECT ord, section_id, section_kind, heading_html, card_only
                         FROM resume_sections WHERE doc_key=%s ORDER BY ord""", (DOC_KEY,))
        sections = cur.fetchall()
        cur.execute("""SELECT section_id, ord, html FROM resume_blocks
                        WHERE doc_key=%s AND retired_at IS NULL
                        ORDER BY section_id, ord""", (DOC_KEY,))
        blocks = cur.fetchall()

    by_section: dict[str, list[dict]] = {}
    for b in blocks:
        by_section.setdefault(b["section_id"], []).append(b)
    for s in sections:
        s["blocks"] = by_section.get(s["section_id"], [])
        s["heading"] = f"{s['ord']}. {s['heading_html']}"

    # ⛔ The contract, asserted before a byte is written. A misspelt or empty id
    # is skipped silently by the exporter and the export still reports success.
    present = {s["section_id"]: s["blocks"] for s in sections}
    broken = [i for i in CONTRACT_IDS if not present.get(i)]
    if broken:
        raise SystemExit(f"[resume-db] REFUSING to write: parser-contract sections "
                         f"missing or empty: {broken}")

    # The education sentence: 'credential, institution (dates).' One place, and
    # the template joins them with newlines exactly as the file writes them.
    education_lines = [f"{_esc(e['credential'])}, {_esc(e['institution'])} "
                       f"({_esc(e['date_range'])})." for e in education]

    out = _env().get_template("master_resume.html.j2").render(
        doc=doc, roles=roles, education=education, education_lines=education_lines,
        profile=profile, sections=sections)

    if "&lt;strong&gt;" in out or "<strong>" not in out:
        raise SystemExit("[resume-db] REFUSING to write: autoescape corrupted the "
                         "bullet HTML (no <strong> survived)")
    return out


def generate(out_path: Path, quiet: bool = False) -> str:
    # ⛔ The master file is never written by this tool. It is the thing the
    # generated output is CHECKED AGAINST; promoting a generated file over it is
    # a decision for the session, taken by hand, after reading the diff.
    if out_path.resolve() == MASTER.resolve():
        raise SystemExit(f"[resume-db] REFUSING to write {MASTER} — generate to "
                         f"{GENERATED.name} and promote it by hand after reading the diff")
    text = render()

    # CLAUDE.md's measurement traps: `src="../static/copy.js"` resolving nowhere
    # left every copy button on every tailored résumé dead through six
    # workspaces, because a missing script throws nothing.
    m = re.search(r'<script src="([^"]+)"', text)
    if m and not (out_path.parent / m.group(1)).resolve().exists():
        raise SystemExit(f"[resume-db] REFUSING to write: script src {m.group(1)!r} "
                         f"does not resolve from {out_path.parent}")

    # Atomic: a generator interrupted halfway through the file he is about to
    # export from is worse than one that did not run.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="",
                                     dir=out_path.parent, delete=False) as fh:
        fh.write(text)
        tmp = Path(fh.name)
    tmp.replace(out_path)
    if not quiet:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"[resume-db] wrote {out_path} ({len(text.encode('utf-8')):,} bytes, "
              f"sha256 {digest[:8]}…)")
    return text


# ---------------------------------------------------------------------------
# verify — THE GATE
# ---------------------------------------------------------------------------
# DESIGN-bullets.md, and CLAUDE.md quoting it: "it must ROUND-TRIP. Parse the
# master into the table, regenerate the HTML, and diff. Byte-identical, or every
# difference enumerated and justified. A lossy migration is the worst outcome
# available; stop rather than proceed."

def _count(pattern: str, text: str) -> int:
    """grep -o | wc -l, never grep -c. These files are effectively minified and
    a line counter reported 4 where there were 63."""
    return len(re.findall(pattern, text))


def verify(out_path: Path) -> int:
    # The file has been rewritten by hand three times in four minutes today.
    # Read it ONCE, load from those exact bytes, and diff against those exact
    # bytes: a gate run against a moving target proves nothing.
    original = MASTER.read_text(encoding="utf-8")
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
    print(f"{'=' * 68}\n  DRIFT GATE — {MASTER}\n{'=' * 68}")
    print(f"  snapshot sha256 : {digest}")
    print(f"  bytes           : {len(original.encode('utf-8')):,}")

    # ⛔ READ-ONLY. This function MUST NOT call load_from().
    #
    # It used to. That made "BYTE-IDENTICAL" a tautology that could not fail —
    # it imported the file into the database and then compared the render against
    # that same file — and it SILENTLY DESTROYED every edit made in the database,
    # which is the one thing the DB-as-source model exists to make possible
    # ("if any changes are needed, you can make those changes to the DB").
    # Proven by mutation on 2026-08-27: a DB-only edit vanished and the gate
    # still printed a pass.
    #
    # What this gate actually asks is the useful question: does the DATABASE, as
    # it stands right now, still reproduce the file on disk? If not, one of them
    # has moved and a human decides which.
    generated = generate(out_path, quiet=True)

    print(f"  rendered from   : database (no reload — this gate never writes to it)")
    print(f"  generated       : {out_path}")
    print(f"  generated bytes : {len(generated.encode('utf-8')):,}")

    checks = [
        ("<strong> open",  r"<strong>"),
        ("<strong> close", r"</strong>"),
        ("<p> open",       r"<p>"),
        ("<li>",           r"<li>"),
        ("section divs",   r'<div class="section copy-target"'),
        ("copy buttons",   r'data-copy-html="1"'),
        ("&amp;",          r"&amp;"),
        ("&mdash;",        r"&mdash;"),
        ("&ndash;",        r"&ndash;"),
    ]
    print(f"\n  {'element':<18} {'master':>8} {'generated':>10}")
    parity = True
    for label, pat in checks:
        a, b = _count(pat, original), _count(pat, generated)
        flag = "" if a == b else "   <-- DIFFERS"
        parity &= a == b
        print(f"  {label:<18} {a:>8} {b:>10}{flag}")
    bare_amp = (_count(r"&(?![A-Za-z][A-Za-z0-9]*;|#)", original),
                _count(r"&(?![A-Za-z][A-Za-z0-9]*;|#)", generated))
    print(f"  {'bare & (unescaped)':<18} {bare_amp[0]:>8} {bare_amp[1]:>10}"
          f"{'' if bare_amp[0] == bare_amp[1] else '   <-- DIFFERS'}")
    parity &= bare_amp[0] == bare_amp[1]

    if generated == original:
        print("\n  ✅ BYTE-IDENTICAL. 0 differences in text, tags, attributes, "
              "entities or whitespace.")
        return 0 if parity else 1

    a, b = original.split("\n"), generated.split("\n")
    diff = list(difflib.unified_diff(a, b, "master (on disk)", "generated", lineterm="", n=0))
    changed = [(i, x, y) for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
    print(f"\n  ⛔ NOT BYTE-IDENTICAL — {len(a)} vs {len(b)} lines, "
          f"{len(changed)} differing line(s). Every one, in full:\n")
    for n, x, y in changed:
        print(f"  line {n}\n    master    : {x}\n    generated : {y}\n")
    if len(a) != len(b):
        print("  (line counts differ — full unified diff follows)")
        for line in diff:
            print("  " + line)
    return 1


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="The master résumé: stored in jobs_tracker_v2, rendered from it.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_load = sub.add_parser("load", help="parse master/upgrad_resume.html into the DB")
    p_load.add_argument("--file", type=Path, default=MASTER,
                        help=f"source to parse (default {MASTER})")

    p_gen = sub.add_parser("generate", help="render the DB back to HTML")
    p_gen.add_argument("--out", type=Path, default=GENERATED,
                       help=f"output path (default {GENERATED})")

    p_ver = sub.add_parser("verify", help="render from the DB and diff against the master (READ-ONLY)")
    p_ver.add_argument("--out", type=Path, default=GENERATED,
                       help=f"where to write the regenerated file (default {GENERATED})")

    args = ap.parse_args()
    try:
        if args.cmd == "load":
            load_from(args.file)
            return 0
        if args.cmd == "generate":
            generate(args.out)
            return 0
        return verify(args.out)
    except ParseError as exc:
        print(f"[resume-db] REFUSING: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
