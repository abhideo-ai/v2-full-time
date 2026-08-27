#!/usr/bin/env python3
"""Every requirement the .docx must meet, in one runnable gate.

They accumulated across 2026-08-27 — from CLAUDE.md, resume-issues-to-avoid/, the
database migration, and a dozen of his own decisions. Spread across four
documents and a conversation, "does it meet our requirements" is unanswerable.
Here they are executable, so the answer is measured rather than recalled.

    automation/.venv/bin/python automation/verify_resume_docx.py [path]

Exit 0 = every checkable requirement met. Exit 1 = at least one failed.
One requirement is deliberately NOT checkable here and says so: the 3-page cap.
"""
import re, sys, zipfile, subprocess, collections, pathlib, html as _html

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCX = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "master/Abhisheik_Deo_Resume.docx"
DSN = "dbname=jobs_tracker_v2"

ok, bad, skip = [], [], []
def req(name, passed, detail=""):
    (ok if passed else bad).append((name, detail))

def q(sql):
    out = subprocess.run(["psql", "-d", "jobs_tracker_v2", "-t", "-A", "-F", "\x1f", "-c", sql],
                         capture_output=True, text=True)
    return [l.split("\x1f") for l in out.stdout.strip().split("\n") if l]

def strip_tags(h):
    return _html.unescape(re.sub(r"<[^>]+>", "", h))

z = zipfile.ZipFile(DOCX)
doc = z.read("word/document.xml").decode()
styles = z.read("word/styles.xml").decode()
core = z.read("docProps/core.xml").decode()
names = z.namelist()

# visible text, paragraph by paragraph
paras = []
for p in re.findall(r"<w:p\b.*?</w:p>", doc, re.S):
    t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
    paras.append({"text": _html.unescape(t), "xml": p,
                  "bullet": "<w:numPr>" in p,
                  "style": (re.search(r'<w:pStyle w:val="([^"]+)"', p) or [None, "Normal"])[1]})
text = "\n".join(p["text"] for p in paras)

# ── CONTENT: every live block byte-identical to the database ────────────────
blocks = q("select section_id, html from resume_blocks where doc_key='master' "
           "and retired_at is null order by section_id, ord")
db_texts = [strip_tags(h) for _, h in blocks]
missing = [t for t in db_texts if t not in text]
req("every database block present, byte-identical", not missing,
    f"{len(db_texts)} blocks; {len(missing)} missing" + (f" e.g. {missing[0][:60]!r}" if missing else ""))

# ── CONTENT: bold, by OCCURRENCE not membership ─────────────────────────────
db_spans = []
for _, h in blocks:
    db_spans += [_html.unescape(re.sub(r"<[^>]+>", "", m)) for m in re.findall(r"<strong>(.*?)</strong>", h, re.S)]
doc_bold = []
for r in re.findall(r"<w:r\b.*?</w:r>", doc, re.S):
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", r, re.S)
    on = rpr and re.search(r'<w:b(?: [^/]*)?/>', rpr.group(0)) and 'w:val="0"' not in rpr.group(0)
    if on:
        doc_bold.append(_html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r))))
want, have = collections.Counter(db_spans), collections.Counter(doc_bold)
short = {k: want[k] - have.get(k, 0) for k in want if want[k] > have.get(k, 0)}
req("every <strong> occurrence is bold (multiplicity, not membership)", not short,
    f"{len(db_spans)} spans, {len(set(db_spans))} distinct; shortfall {sum(short.values())}")

# ── CONTENT: the facts he settled, and no stale content ─────────────────────
for term, want_present in [("AngularJS", True), ("280", True), ("Aurora", True), ("Apr 2026", True),
                           ("Knockout", False), ("Product & Platform Strategy", False),
                           ("300+", False)]:
    present = term in text
    req(f"{'contains' if want_present else 'does NOT contain'} {term!r}", present == want_present)
req("no bare 'Angular' (must be AngularJS)", not re.search(r"Angular(?!JS)", text))
req("no [fill in metric] placeholder", "[fill in metric]" not in text)

# ── CONTENT: contact + education ────────────────────────────────────────────
for label, needle in [("phone", "93640 27487"), ("email", "abhisheik@abhideo.ai"),
                      ("LinkedIn slug", "abhisheikdeo"), ("location", "Hyderabad"),
                      ("MS Computer Science", "University of Houston"), ("PG Diploma", "IIIT")]:
    req(f"contact/education: {label}", needle in text)
req("LinkedIn is a real hyperlink", "<w:hyperlink" in doc)

# ── CONTENT: sections and roles ─────────────────────────────────────────────
nsec = int(q("select count(*) from resume_sections where doc_key='master'")[0][0])
nrole = int(q("select count(*) from resume_roles where doc_key='master'")[0][0])
roles = q("select company, role_title from resume_roles where doc_key='master' order by n")
missing_roles = [c for c, t in roles if c not in text]
req(f"all {nrole} roles present", not missing_roles, f"missing: {missing_roles}")

# ── HYGIENE: word count, trailing periods, verbs ────────────────────────────
def words(t): return [w for w in re.split(r"\s+", t) if re.search(r"[A-Za-z0-9]", w)]
exp = [strip_tags(h) for sid, h in blocks
       if sid in ("quick-vp","quick-deque","quick-rocket","quick-voltuswave-cofounder",
                  "quick-teletext","p-cura","p-innroad","p-mcd","p-elpaso","p-lynton")]
over = [t for t in exp if len(words(t)) > 25]
req("no experience bullet over 25 words (punctuation-aware)", not over, f"{len(over)} over")
periods = [t for t in exp if t.rstrip().endswith(".")]
req("no trailing periods on bullets", not periods, f"{len(periods)} with a period")
verbs = [words(t)[0].rstrip(",") for t in exp if words(t)]
dupes = [v for v, n in collections.Counter(verbs).items() if n > 1]
req(f"{len(verbs)} experience bullets, all leading verbs distinct", not dupes, f"dupes: {dupes}")

BANNED = ["Kafka","NATS","MongoDB","ClickHouse","Azure","Google Cloud","SOC 2",
          "Spring Cloud","Spring WebFlux","Spring Batch","Grafana","Prometheus","Hazelcast"]
hits = [b for b in BANNED if re.search(r"\b"+re.escape(b)+r"\b", text, re.I)]
req("no banned technology", not hits, f"hits: {hits}")
req("no 'six continuous years' of Spring Boot", not re.search(r"six\s+continuous", text, re.I))

# ── ATS SAFETY ──────────────────────────────────────────────────────────────
req("zero layout tables", "<w:tbl>" not in doc)
req("zero text boxes", "txbxContent" not in doc)
req("zero embedded images", not [n for n in names if n.startswith("word/media/")])
req("single column", not re.search(r'<w:cols [^>]*w:num="[2-9]"', doc))
# Bullets may come from a per-paragraph <w:numPr> OR from the applied list
# STYLE carrying it. The style-driven form is the better one — it is why Word's
# style pane can restyle every bullet at once — so demanding inline numPr marked
# a correct file as broken. What actually matters: real list numbering somewhere,
# and no literal "•" typed into the text.
_list_styles = re.findall(r'<w:style [^>]*w:styleId="(?:ListBullet|ListParagraph)".*?</w:style>',
                          styles, re.S)
_numbered = ("<w:numPr>" in doc) or any("<w:numPr>" in b for b in _list_styles)
req("real bullet lists, not literal bullet characters", _numbered and "•" not in text,
    f"inline numPr={doc.count('<w:numPr>')}, style-driven={any('<w:numPr>' in b for b in _list_styles)}, "
    f"literal bullets={text.count('•')}")

# ── EDITABILITY ─────────────────────────────────────────────────────────────
boff = len(re.findall(r'<w:b w:val="0"/>', doc))
req("no explicit bold-OFF overrides (Word style pane works)", boff == 0, f"{boff} found")
used = set(re.findall(r'<w:pStyle w:val="([^"]+)"', doc))
req("uses built-in style names", bool(used & {"Heading1","Heading2","Heading3","ListBullet",
                                              "Heading 1","Heading 2","Heading 3","List Bullet"}),
    f"styles: {sorted(used)}")
req("docProps say Abhisheik Deo, not python-docx",
    "python-docx" not in core and "Abhisheik Deo" in core)

# ── FORMAT (his reference) ──────────────────────────────────────────────────
pg = re.search(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"', doc)
req("A4 page size", bool(pg) and abs(int(pg.group(1))-11906) < 40, pg.group(0) if pg else "none")
mar = re.search(r'<w:pgMar[^/]*/>', doc)
req("page margins present", bool(mar), mar.group(0) if mar else "none")
blue = len(re.findall(r'w:val="328EF7"', doc)) + len(re.findall(r'w:val="328EF7"', styles))
req("heading colour #328EF7 (his format)", blue > 0, f"{blue} uses")

skip.append(("3 pages or fewer",
             "NOT CHECKABLE HERE — no LibreOffice on this machine, and the only prior "
             "export was the 39-bullet version. Open it in Word."))

# ── report ──────────────────────────────────────────────────────────────────
print(f"{'='*74}\n  REQUIREMENTS — {DOCX.name}\n{'='*74}")
for n, d in ok:   print(f"  ✅ {n}" + (f"  ({d})" if d else ""))
for n, d in bad:  print(f"  ⛔ {n}" + (f"  ({d})" if d else ""))
for n, d in skip: print(f"  ⏸  {n}\n       {d}")
print(f"\n  {len(ok)} met · {len(bad)} FAILED · {len(skip)} not checkable here")
sys.exit(1 if bad else 0)
