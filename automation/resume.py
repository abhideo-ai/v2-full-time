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
    paste into, a per-workspace favicon so open tabs stay tellable apart, and
    the launcher card so the workspace is reachable and counted.
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

    shutil.copy(master, dest_dir / "upgrad_resume.html")
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

    # Register on the launcher so it is reachable and counted in the tabs.
    idx = ROOT / "index.html"
    s = idx.read_text()
    href = f"{rel.as_posix()}/index.html"
    if href not in s:
        card = (f'    <a class="card" data-status="building" href="{href}">\n'
                f'      <strong>{title}</strong><span class="path">{rel.as_posix()}/</span></a>\n')
        anchor = '  <div class="grid" id="app-list">\n'
        if anchor in s:
            idx.write_text(s.replace(anchor, anchor + card, 1))
        else:
            print("[resume] WARNING: could not find #app-list — add the launcher card by hand",
                  file=sys.stderr)

    print(f"[resume] created {rel}/")
    for f in ("upgrad_resume.html", "jd.md", "paste_notes.json"):
        print(f"[resume]   {f}")
    print(f"[resume] registered on the launcher as \"building\"")
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
        body = "\n        ".join(f"<p>{p}</p>" for p in now)
        blocks.append(f'''<h3 class="section-head">{i + 1}. {title}</h3>

  <section class="{cls}">
    <h3 class="paste-block-title"><span class="num">{NUMS[i]}</span><span class="label">{tag}</span> {title}</h3>
    <p class="paste-block-why"><strong>Why:</strong> {why}</p>
    <p class="paste-block-heads-up"><strong>Heads-up:</strong> {heads}</p>
    <p class="paste-block-hygiene"><strong>Hygiene:</strong> {hyg}</p>
    <div class="paste-area copy-target" id="sec-{sec_id}">
      <button type="button" class="copy-btn" data-copy-target="#sec-{sec_id}" data-copy-html="1">Copy whole section →</button>
        {body}
    </div>
  </section>''')

    up = "../" * len(src.parent.relative_to(ROOT).parts)
    out = src.parent / "paste_sheet.html"
    out.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{H.escape(label)} — section-by-section paste</title>
  <link rel="stylesheet" href="{up}style.css" />
</head>
<body>
<main class="page" id="main">

<p class="breadcrumb"><a href="{up}index.html">Full-time JD workspace</a> · {H.escape(label)} · paste sheet</p>

<header>
  <p class="eyebrow">Card build · {changed} of 10 sections changed since {H.escape(since)}</p>
  <h1>Paste into the Hiration card, section by section</h1>
</header>

<div class="tldr">
  <strong>One button, one whole section, one paste</strong>
  Every block is a <em>complete</em> section that replaces its counterpart outright — select the
  section in Hiration, delete it, paste. Never a fragment to merge into an existing block. Use the
  button, not a manual selection: upGrad silently drops bold from a hand-dragged copy and you will
  not see it until the exported PDF.
</div>

<div class="callout">
  <b>Generated</b> from <code>{H.escape(src.relative_to(ROOT).as_posix())}</code> by
  <code>automation/resume.py sheet</code>. Which sections changed is derived by diffing against <code>{H.escape(since)}</code>, so it cannot go stale. Do not edit this page — edit the résumé and regenerate.
</div>

<h2 class="quick-paste-title">Section by section</h2>

  {"".join(chr(10) + chr(10) + "  <!-- ============================================================ -->" + chr(10) + "  " + b for b in blocks)}

<footer class="signoff">
  <p><a href="{H.escape(src.name)}">The résumé</a> · regenerate with
     <code>automation/resume.py sheet{f" --slug {label}" if slug else ""}</code></p>
</footer>

</main>
<script src="{up}static/copy.js" defer></script>
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
