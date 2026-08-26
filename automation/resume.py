#!/usr/bin/env python3
"""Make a new résumé, and make its paste sheet.

    automation/.venv/bin/python automation/resume.py new   --slug <slug>
    automation/.venv/bin/python automation/resume.py sheet [--slug <slug>]

`new`   copies the master résumé into a workspace so a per-job résumé starts
        from the master instead of from a blank file or a stale copy.
`sheet` emits <workspace>/paste_sheet.html — every section as ONE copy block.

THE RULE THIS ENFORCES: a copy block is one COMPLETE section that replaces its
counterpart wholesale, never a fragment to merge into an existing block. A
partial paste means reading the existing block, working out where the new text
goes, and not duplicating what is already there — three chances to get it wrong
silently, in a field that cannot easily be diffed afterwards.

Copy blocks are GENERATED FROM the résumé file, never retyped, so the sheet
cannot disagree with what the bot will write.

Which sections changed is derived by diffing against the last committed version
in git, so nobody has to remember. The *reason* each changed cannot be derived;
it is read from an optional sidecar, <workspace>/paste_notes.json:

    {"quick-summary": {"why": "...", "heads_up": "...", "hygiene": "..."}}

A section that changed with no note says so plainly rather than inventing one.
"""
import argparse
import html as H
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from upgrad_resume_paste import _resolve_resume_paste  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NUMS = "①②③④⑤⑥⑦⑧⑨⑩"

SECTIONS = [
    ("quick-headline", "Headline"),
    ("quick-summary", "Summary"),
    ("quick-skills-tls", "Skills — Technology Leadership &amp; Strategy"),
    ("quick-skills-ee", "Skills — Engineering Excellence"),
    ("quick-skills-bd", "Skills — Business &amp; Delivery"),
    ("quick-vp", "VoltusWave — Principal Software Architect"),
    ("quick-deque", "Deque Software"),
    ("quick-rocket", "Rocket Software"),
    ("quick-voltuswave-cofounder", "VoltusWave — Co-Founder &amp; VP of Technology"),
    ("quick-teletext", "Teletext India"),
]


def paragraphs(html: str, sec_id: str) -> list[str]:
    """Every <p> in a section, copy button stripped. Also reads <ul><li>."""
    m = re.search(rf'id="{sec_id}"(.*?)</div>', html, re.S)
    if not m:
        return []
    body = re.sub(r"<button.*?</button>", "", m.group(1), flags=re.S)
    items = re.findall(r"<li>(.*?)</li>", body, re.S) or re.findall(r"<p>(.*?)</p>", body, re.S)
    return [" ".join(i.split()) for i in items if i.strip()]


def committed(path: Path, ref: str = "HEAD") -> str | None:
    """`path` as of a git ref, or None if it did not exist there.

    Defaults to HEAD. Pass --since when the changes are already committed and
    the interesting baseline is further back — diffing a committed file against
    HEAD correctly reports nothing changed, which is useless for a paste sheet
    whose whole job is to say what changed.
    """
    rel = path.relative_to(ROOT).as_posix()
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def cmd_new(slug: str, company: str | None = None, role: str | None = None) -> None:
    """Scaffold a full job workspace, résumé seeded from the master.

    Everything repeated 15-20 times a night belongs here, not in a human's
    hands: the directory, the résumé copy, the empty notes sidecar, a jd.md to
    paste into, a per-workspace favicon so open tabs stay tellable apart, and a
    row in `jobs_tracker_v2` so the seat is reachable, countable and queryable.
    """
    master = ROOT / "master" / "upgrad_resume.html"
    if not master.exists():
        raise SystemExit(f"[resume] no master at {master}")
    today = date.today()
    rel = Path(today.strftime("%B-%Y")) / today.strftime("%d") / slug
    dest_dir = ROOT / rel
    if (dest_dir / "upgrad_resume.html").exists():
        raise SystemExit(f"[resume] {rel}/upgrad_resume.html exists — refusing to overwrite")
    dest_dir.mkdir(parents=True, exist_ok=True)

    # The master lives at master/, so its stylesheet href is "../style.css".
    # A workspace sits at Month-YYYY/DD/<slug>/, three levels down, so a straight
    # copy leaves a dead link and the résumé renders unstyled when he opens it.
    # The exporter does not care -- it reads text -- but he reviews these by eye.
    up = "../" * len(rel.parts)
    dest = dest_dir / "upgrad_resume.html"
    dest.write_text(
        master.read_text(encoding="utf-8").replace('href="../style.css"', f'href="{up}style.css"'),
        encoding="utf-8")
    (dest_dir / "paste_notes.json").write_text("{}\n")
    title = f"{company} — {role}" if company and role else slug
    (dest_dir / "jd.md").write_text(
        f"# {title}\n\n<!-- Paste the job description here verbatim. URL, location, comp if stated. -->\n")

    # Per-workspace favicon: 15-20 open tabs are indistinguishable otherwise.
    try:
        subprocess.run([sys.executable, str(ROOT / "automation" / "workspace_favicon.py"),
                        "--slug", slug], cwd=ROOT, capture_output=True, check=False)
    except Exception:                                            # noqa: BLE001
        pass

    # Register in jobs_tracker_v2 so the seat is reachable, countable and
    # QUERYABLE. This used to append a card to index.html; the launcher now
    # renders from the database, so writing markup here would produce a row
    # nothing can search. A failure is a warning, never fatal — the workspace on
    # disk is the valuable part, and `jobs_sync.py` can register it afterwards.
    registered = False
    try:
        import jobs_sync
        registered = jobs_sync.register(
            slug,
            company or slug,
            role or "[role]",
            status="resume_drafted",
            source_url=f"(no URL supplied — workspace {rel.as_posix()})",
        )
    except Exception as exc:                                     # noqa: BLE001
        print(f"[resume] WARNING: could not register {slug} in jobs_tracker_v2 ({exc})",
              file=sys.stderr)
        print("[resume]          fix the database, then: jobs_sync.py", file=sys.stderr)

    print(f"[resume] created {rel}/")
    for f in ("upgrad_resume.html", "jd.md", "paste_notes.json"):
        print(f"[resume]   {f}")
    if registered:
        print('[resume] registered in jobs_tracker_v2 as "resume_drafted"'
              ' — shows under "Ready to apply"')
    else:
        print(f"[resume] {slug} was already in jobs_tracker_v2 — left as it stands")
    print(f"[resume] next: paste the JD into {rel}/jd.md, re-vector per Rule 7,")
    print(f"[resume]       then: resume.py sheet --slug {slug}")


def cmd_sheet(slug: str | None, since: str = "HEAD") -> None:
    if slug:
        src = _resolve_resume_paste(slug, ROOT)
        label = slug
    else:
        src = ROOT / "master" / "upgrad_resume.html"
        label = "master"
    if not src.exists():
        raise SystemExit(f"[resume] no résumé at {src}")
    html = src.read_text()
    prev = committed(src, since)
    notes = {}
    np = src.parent / "paste_notes.json"
    if np.exists():
        notes = json.loads(np.read_text() or "{}")

    blocks, changed = [], 0
    for i, (sec_id, title) in enumerate(SECTIONS):
        # Key Skills renders as one section on the card and is replaced whole,
        # so only the combined block is emitted — three separate ones invite
        # exactly the partial paste the whole-section rule forbids.
        if sec_id.startswith('quick-skills-'):
            continue
        now = paragraphs(html, sec_id)
        if not now:
            print(f"[resume] WARNING: {sec_id} is empty — the parser will skip it silently",
                  file=sys.stderr)
        was = paragraphs(prev, sec_id) if prev else None
        is_new = was is None
        diff = is_new or was != now
        if diff and not is_new:
            changed += 1
        n = notes.get(sec_id, {})
        why = n.get("why") or (
            "New file — no previous version to compare against." if is_new else
            "<strong>Changed, but no reason recorded.</strong> Add one to "
            f"<code>paste_notes.json</code> under <code>{sec_id}</code>." if diff else
            f"Unchanged since <code>{H.escape(since)}</code>. Included so the whole card can be built from one page.")
        heads = n.get("heads_up") or (
            "Replaces the <strong>whole</strong> section. Select it in Hiration, delete it, paste."
            if diff else "Unchanged — paste only if you are rebuilding the card from scratch.")
        hyg = n.get("hygiene") or f"{len(now)} line(s)"
        tag = "Replace:" if diff else "No change:"
        cls = "paste-block" if diff else "paste-block nochange"
        # ONE <p> PER COPY BLOCK. Both halves of this are load-bearing and
        # v1 learned them the hard way (v1 CLAUDE.md, bullets_for_upgrad):
        #
        #   <ul><li> together  -> upGrad STRIPS THE BOLD
        #   <p> together       -> collapses into a single line
        #   <p> one at a time  -> works
        #
        # So a bullet section cannot have a whole-section button at all; the
        # many small buttons ARE the mechanism, not clutter.
        rows = "\n        ".join(
            f'<div class="bullet-row">'
            f'<div class="paste-area copy-target" id="b-{sec_id}-{j}">'
            f'<button type="button" class="copy-btn mini" data-copy-target="#b-{sec_id}-{j}" '
            f'data-copy-html="1">copy</button><p>{x}</p></div></div>'
            for j, x in enumerate(now, 1))
        # Section-level copy needs a source with NO wrapper markup, so it gets
        # its own hidden div holding only the <p>s. copy.js builds the clipboard
        # from innerHTML, so `hidden` costs nothing and keeps the page clean.
        # WHOLE-SECTION source is <ul><li>, COMPACT. <p> per line keeps bold but
        # loses the bullets; <ul><li> keeps the bullets. The earlier <ul> test
        # that lost bold ran BEFORE whitespace between <ul> and <li> was
        # stripped — a text node where a list expects only <li> children makes a
        # sanitiser fall back to plain text, which is exactly "bullets kept,
        # bold lost". No whitespace here, so the list parses as a list.
        hidden_src = "<ul>" + "".join(f"<li>{x}</li>" for x in now) + "</ul>"
        body = (f'<div class="paste-area copy-target sr-src" id="sec-{sec_id}" hidden>'
                f'{hidden_src}</div>\n        ' + rows)
        blocks.append(f'''<div class="ps-head">
    <h3 class="section-head">{i + 1}. {title}</h3>
    <label><input type="checkbox" class="ps-done" data-sec="{sec_id}" /> pasted</label>
  </div>

  <section class="{cls}">
    <h3 class="paste-block-title"><span class="num">{NUMS[i]}</span><span class="label">{tag}</span> {title}</h3>
    <p class="paste-block-why"><strong>Why:</strong> {why}</p>
    <p class="paste-block-heads-up"><strong>Heads-up:</strong> {heads}</p>
    <p class="paste-block-hygiene"><strong>Hygiene:</strong> {hyg}</p>
    <div class="bullet-stack">
      <p class="stack-head">
        <button type="button" class="copy-btn wide" data-copy-target="#sec-{sec_id}" data-copy-html="1">Copy whole section →</button>
        <span class="dim">or copy one line at a time below</span>
      </p>
        {body}
    </div>
  </section>''')

    # Key Skills is three parsed sub-groups but ONE section on the card, and it
    # is replaced whole when tailoring per job — so it gets a combined block.
    ks = [(sid, t.split("— ", 1)[-1]) for sid, t in SECTIONS if sid.startswith("quick-skills-")]
    ks_body = ""
    ks_hidden = ""
    for sid, sub in ks:
        ks_hidden += (f"<p><strong>{sub}</strong></p><ul>"
                      + "".join(f"<li>{x}</li>" for x in paragraphs(html, sid))
                      + "</ul>")
        ks_body += f"\n        <p class=\"ks-group\"><strong>{sub}</strong></p>"
        ks_body += "".join(
            f'\n        <div class="bullet-row">'
            f'<div class="paste-area copy-target" id="b-{sid}-{j}">'
            f'<button type="button" class="copy-btn mini" data-copy-target="#b-{sid}-{j}" '
            f'data-copy-html="1">copy</button><p>{x}</p></div></div>'
            for j, x in enumerate(paragraphs(html, sid), 1))
    combined = f'''<h3 class="section-head">Key Skills — all three groups, one paste</h3>

  <section class="paste-block">
    <h3 class="paste-block-title"><span class="num">★</span><span class="label">Replace:</span> the entire Key Skills section</h3>
    <p class="paste-block-why"><strong>Why:</strong> Key Skills is three sub-groups on the card but
    <strong>one section</strong>, and when tailoring per job it is replaced <em>whole</em> — not
    line by line. This block is the whole thing, so you never have to hunt for which sub-group a
    line belongs to.</p>
    <p class="paste-block-heads-up"><strong>Heads-up:</strong> use this <em>or</em> the three
    separate blocks below, never both. The sub-group headings are included; delete them if Hiration
    renders its own.</p>
    <p class="paste-block-hygiene"><strong>Hygiene:</strong> {sum(len(paragraphs(html, sid)) for sid, _ in ks)} lines across 3 groups · short capability labels, not sentences · no number requirement</p>
    <div class="bullet-stack">
      <p class="stack-head">
        <button type="button" class="copy-btn wide" data-copy-target="#sec-key-skills-all" data-copy-html="1">Copy all of Key Skills →</button>
        <span class="dim">or copy one line at a time below</span>
      </p>
      <div class="paste-area copy-target sr-src" id="sec-key-skills-all" hidden>{ks_hidden}</div>{ks_body}
    </div>
  </section>'''
    blocks.insert(2, combined)

    up = "../" * len(src.parent.relative_to(ROOT).parts)
    out = src.parent / "paste_sheet.html"
    out.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{H.escape(label)} — section-by-section paste</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="stylesheet" href="{up}style.css" />
</head>
<body data-sheet="{H.escape(label)}">
<main class="page" id="main">

<p class="breadcrumb"><a href="{up}index.html">Full-time JD workspace</a> · {H.escape(label)} · paste sheet</p>

<header>
  <p class="eyebrow">Card build · {changed} of 10 sections changed since {H.escape(since)}</p>
  <h1>Paste into the Hiration card, section by section</h1>
</header>

<div class="tldr">
  <strong>One button per line — and that is not clutter, it is the only thing that works</strong>
  upGrad <strong>strips bold from a <code>&lt;ul&gt;/&lt;li&gt;</code> paste</strong>, and pasting
  several <code>&lt;p&gt;</code> at once collapses them into a single line. A standalone
  <code>&lt;p&gt;</code> pasted <em>on its own</em> is the one shape that keeps the bold and stays
  a separate bullet. Click <code>copy</code>, paste, next line.
  <strong>Better still, do not paste at all —</strong>
  The exporter writes all ten sections itself — <code>_paste_html</code> hands Hiration's Draft.js
  editor real <code>&lt;ul&gt;&lt;li&gt;</code> with <code>&lt;strong&gt;</code> intact, which is
  how v1 carried formatting across at 100%. Build the card skeleton by hand (dates, El Paso,
  Personal Information, sections 11–15), then run the export at the bottom of this page. These
  blocks are here for reading, for checking what the bot will write, and for the occasional
  one-off fix — one button, one whole section.
  Every block is a <em>complete</em> section that replaces its counterpart outright — select the
  section in Hiration, delete it, paste. Never a fragment to merge into an existing block. Use the
  button, not a manual selection: upGrad silently drops bold from a hand-dragged copy and you will
  not see it until the exported PDF.
</div>

<div class="callout">
  <b>Generated</b> from <code>{H.escape(src.relative_to(ROOT).as_posix())}</code> by
  <code>automation/resume.py sheet</code>. Which sections changed is derived by diffing against <code>{H.escape(since)}</code>, so it cannot go stale. Do not edit this page — edit the résumé and regenerate.
</div>

<div class="ps-bar">
  <span id="ps-count">0/10 pasted</span>
  <button type="button" id="ps-reset">reset</button>
  <span class="dim">Ticks survive a reload, and the tab title shows your progress.</span>
</div>

<h2 class="quick-paste-title">Section by section</h2>

  {"".join(chr(10) + chr(10) + "  <!-- ============================================================ -->" + chr(10) + "  " + b for b in blocks)}

<h2>Card-only — hand-edit these in Hiration</h2>
<p class="lede">The bot never writes any of this. It is in
<a href="{H.escape(src.name)}">the résumé</a> in full; the ones that bite are here.</p>
<ul class="checks">
  <li><strong>Dates.</strong> VoltusWave must read <strong>Apr 2026</strong> (Mar 2025 – Apr 2026).
  Deque Dec 2019 – Feb 2025. Verify after cloning — do not assume the clone kept them.</li>
  <li><strong>El Paso → Senior Java Developer</strong>, JSP and Java Enterprise Edition, Tennessee
  Gas Pipeline. The v1 card calls it <strong>.NET</strong>, which hides four of the eleven Java
  years. This is the single highest-value correction on the card.</li>
  <li><strong>Personal Information modal</strong> — Hyderabad · phone · email · LinkedIn slug
  <strong>abhisheikdeo</strong>, not <code>abhideo</code>, which is the email domain.</li>
  <li><strong>Sections 11–15</strong> — CURA, innRoad, McDonald&#39;s, El Paso, LyntonWeb.</li>
</ul>

<h2>Then export</h2>
<div class="paste-area copy-target" id="sec-export">
  <button type="button" class="copy-btn" data-copy-target="#sec-export">Copy command →</button>
  <p><code>UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py --slug {H.escape(label)} --no-pause --reset</code></p>
</div>
<p class="dim">Run from the repo root — the persistent browser profile lives there, so the working
directory matters. The bot runs serially on one shared browser.</p>

<h2>Verify the PDF</h2>
<ul class="checks">
  <li>Dates correct — VoltusWave ended <strong>Apr 2026</strong></li>
  <li>Bold renders visibly <strong>heavier</strong>, not just a different font</li>
  <li>Contact details, and the LinkedIn slug <strong>abhisheikdeo</strong></li>
  <li>No <code>[fill in metric]</code> anywhere</li>
  <li><strong>At most 3 pages</strong></li>
  <li>Content matches this sheet</li>
</ul>
<p class="dim">Ignore the applicant tracking system &ldquo;Resume Review&rdquo; score — it moves on
hygiene, not on fit.</p>

<footer class="signoff">
  <p><a href="{H.escape(src.name)}">The résumé</a> · regenerate with
     <code>automation/resume.py sheet{f" --slug {label}" if slug else ""}</code></p>
</footer>

</main>
<script src="{up}static/copy.js" defer></script>
<script src="{up}static/paste.js" defer></script>
</body>
</html>
''')
    print(f"[resume] wrote {out.relative_to(ROOT)} — {changed} of 10 sections changed"
          + ("" if prev else " (new file, nothing to diff against)"))


def main() -> None:
    ap = argparse.ArgumentParser(prog="resume", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["new", "sheet"])
    ap.add_argument("--slug", default=None)
    ap.add_argument("--since", default="HEAD", help="git ref to diff against (default HEAD)")
    ap.add_argument("--company", default=None)
    ap.add_argument("--role", default=None)
    a = ap.parse_args()
    if a.command == "new":
        if not a.slug:
            raise SystemExit("[resume] new needs --slug")
        cmd_new(a.slug, a.company, a.role)
    else:
        cmd_sheet(a.slug, a.since)


if __name__ == "__main__":
    main()
