#!/usr/bin/env python3
"""Render daily/index.html from daily/days.json.

    automation/.venv/bin/python automation/daily.py

The log is regenerated every day, so the HTML is derived, never authored by
hand: editing days.json is the whole workflow and this file owns the markup.

Two header facts are derived from the repo on every run, so they cannot drift:
the pipeline counts (read from the root launcher's data-status rows) and the
parser pre-flight (the real upgrad_resume_paste parser, run against master/).

`task`, `detail` and `why` are TRUSTED HTML and are deliberately not escaped.

ROLLOVER IS NOT DONE HERE. Checkbox state lives in the browser's localStorage,
which Python cannot see, so static/todo.js derives the rolled-over list at load
time from every earlier day still unticked. days.json never duplicates a task.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
DAYS_JSON = ROOT / "daily" / "days.json"
OUT = ROOT / "daily" / "index.html"

PRIORITY_PILL = {1: "red", 2: "yellow", 3: "fact"}


def load_doc() -> dict:
    doc = json.loads(DAYS_JSON.read_text())
    doc["days"].sort(key=lambda d: d["date"], reverse=True)
    return doc


def validate(days: list[dict]) -> None:
    """Fail loudly. Every trap here is otherwise silent in the rendered page."""
    for day in days:
        items = [i for g in day["groups"] for i in g["items"]]
        ids = [i["id"] for i in items]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise SystemExit(f"[daily] {day['date']}: duplicate task ids {sorted(dupes)}")
        known = set(ids)
        for item in items:
            if item.get("p", 2) not in PRIORITY_PILL:
                raise SystemExit(
                    f"[daily] {day['date']}/{item['id']}: priority must be 1, 2 or 3"
                )
            unknown = [n for n in item.get("needs", []) if n not in known]
            if unknown:
                raise SystemExit(
                    f"[daily] {day['date']}/{item['id']}: needs unknown task(s) {unknown}"
                )
        # cycle check
        needs = {i["id"]: list(i.get("needs", [])) for i in items}
        seen, stack = set(), set()

        def walk(node: str) -> None:
            if node in stack:
                raise SystemExit(f"[daily] {day['date']}: dependency cycle at {node!r}")
            if node in seen:
                return
            stack.add(node)
            for nxt in needs[node]:
                walk(nxt)
            stack.discard(node)
            seen.add(node)

        for node in needs:
            walk(node)


def pipeline_stats() -> dict:
    """Counts from the root launcher, which is the pipeline's own record."""
    html = (ROOT / "index.html").read_text()
    # Strip HTML comments FIRST: the launcher keeps a commented-out example card
    # carrying data-status="ready", and counting it reported a phantom workspace.
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    app_list = re.search(r'id="app-list"(.*?)</div>', html, re.S)
    rows = re.findall(r'data-status="([a-z-]+)"', app_list.group(1) if app_list else "")
    return {"total": len(rows), "ready": rows.count("ready"), "sent": rows.count("sent")}


def preflight() -> dict:
    """Run the REAL parser against master/, so this can never claim a stale pass."""
    try:
        from upgrad_resume_paste import parse_slug
        parsed = parse_slug("master")
    except Exception as exc:                                    # noqa: BLE001
        return {"ok": False, "why": f"{type(exc).__name__}: {exc}"}
    counts = [len(b) for _, b in parsed["skills"]]
    exp = [len(e[1] if isinstance(e, tuple) else e.get("bullets", [])) for e in parsed["experience"]]
    src = (ROOT / "master" / "upgrad_resume.html").read_text()
    ids = sorted(set(re.findall(r'id="(quick-[a-z-]+)"', src)))
    return {
        "ok": len(ids) == 10 and "[fill in metric]" not in src,
        "ids": len(ids),
        "skills": counts,
        "exp": exp,
        "bullets": sum(exp),
        "placeholders": src.count("[fill in metric]"),
    }


def render_item(item: dict, day: str) -> str:
    prio = item.get("p", 2)
    needs = item.get("needs", [])
    due = item.get("due", day)          # no explicit due date -> due on its own day
    # `t` prefix: an id starting with a digit is legal HTML but is NOT a valid
    # CSS identifier, so querySelector("#2026...") throws. Prefix, don't escape.
    box_id = f"t{day.replace('-', '')}-{item['id']}"
    needs_html = ""
    if needs:
        needs_html = (
            '<span class="dl-needs">after '
            + ", ".join(f"<code>{n}</code>" for n in needs)
            + "</span>"
        )
    detail = f'<span class="dl-detail">{item["detail"]}</span>' if item.get("detail") else ""
    return f"""        <li data-id="{item['id']}" data-needs="{','.join(needs)}" data-p="{prio}" data-due="{due}">
          <input type="checkbox" id="{box_id}" data-id="{item['id']}" />
          <label for="{box_id}">
            <span class="dl-task">{item['task']}</span>
            <span class="dl-meta"><span class="pill {PRIORITY_PILL[prio]}">P{prio}</span>{needs_html}</span>
            {detail}
          </label>
          <span class="dl-actions">
            <button type="button" class="dl-act" data-act="parked" title="Park with a reason">Park</button>
            <button type="button" class="dl-act" data-act="pushed" title="Push to a later day">Push</button>
            <button type="button" class="dl-act" data-act="dropped" title="Drop for good">Drop</button>
            <button type="button" class="dl-act restore" data-act="restored" title="Put it back">Restore</button>
          </span>
        </li>"""


def render_group(group: dict, day: str) -> str:
    kind = f" {group['kind']}" if group.get("kind") else ""
    why = f'      <p class="dl-why">{group["why"]}</p>\n' if group.get("why") else ""
    items = "\n".join(render_item(i, day) for i in group["items"])
    return f"""    <div class="dl-group{kind}">
      <h3>{group['title']}</h3>
{why}      <ul class="dl-list">
{items}
      </ul>
    </div>"""


def render_callout(callout: dict) -> str:
    kind = f" {callout['kind']}" if callout.get("kind") else ""
    return (
        f'    <div class="callout{kind}">\n'
        f'      <b>{callout["title"]}</b> {callout["body"]}\n'
        f"    </div>"
    )


def preflight_callout(pf: dict) -> str:
    if not pf.get("ok"):
        return (
            '    <div class="callout bad">\n'
            "      <b>Pre-flight FAILED.</b> The parser could not read "
            "<code>master/upgrad_resume.html</code> cleanly, so an export would ship whatever "
            f"it managed to parse: {pf.get('why', '')} "
            f"ids={pf.get('ids', '?')}/10, "
            f"<code>[fill in metric]</code>×{pf.get('placeholders', '?')}. Fix this before "
            "exporting anything.\n    </div>"
        )
    return (
        '    <div class="callout good">\n'
        "      <b>Pre-flight green — no action needed.</b> Checked on this render, not quoted "
        f"from memory: all <strong>{pf['ids']}</strong> <code>quick-*</code> ids present in "
        "<code>master/upgrad_resume.html</code>, all parse with no silent skip, skills "
        f"{' · '.join(str(c) for c in pf['skills'])} and experience "
        f"{' · '.join(str(c) for c in pf['exp'])} = <strong>{pf['bullets']}</strong> bullets, "
        "zero <code>[fill in metric]</code>. Nothing in the HTML is blocking an export — only "
        "the card is.\n    </div>"
    )


def render_day(day: dict, is_today: bool, pf: dict) -> str:
    pretty = date.fromisoformat(day["date"]).strftime("%a %d %b %Y").replace(" 0", " ")
    classes = "dl-day today" if is_today else "dl-day"
    today_pill = ' <span class="pill note">today</span>' if is_today else ""
    rolled = (
        '    <div class="dl-group rolled" id="rolled-over" hidden>\n'
        "      <h3>Rolled over — unfinished from an earlier day</h3>\n"
        '      <p class="dl-why">Carried forward automatically from every earlier day still '
        "unticked. Tick one here and it ticks on its original day too.</p>\n"
        '      <ul class="dl-list"></ul>\n'
        "    </div>"
        if is_today
        else ""
    )
    next_up = (
        '    <div class="wl-donow" id="next-up" hidden>\n'
        '      <p class="lbl">Do next</p>\n'
        "      <p></p>\n"
        "    </div>"
        if is_today
        else ""
    )
    moved = (
        "\n\n".join(
            f'    <details class="dl-moved" id="moved-{kind}" hidden>\n'
            f'      <summary>{title} <span class="n">0</span></summary>\n'
            f'      <ul class="dl-list"></ul>\n'
            f"    </details>"
            for kind, title in (
                ("parked", "Parked"), ("pushed", "Pushed to a later day"), ("dropped", "Dropped")
            )
        )
        if is_today
        else ""
    )
    blocks = [b for b in (next_up, rolled) if b]
    blocks += [render_group(g, day["date"]) for g in day["groups"]]
    if is_today:
        blocks.append(preflight_callout(pf))
    blocks += [render_callout(c) for c in day.get("callouts", [])]
    if moved:
        blocks.append(moved)
    body = "\n\n".join(blocks)
    return f"""<details class="{classes}" data-day="{day['date']}"{' open' if is_today else ''}>
  <summary>{pretty}{today_pill}<span class="dl-count"></span></summary>
  <div class="dl-body">

{body}

  </div>
</details>"""


def main() -> None:
    doc = load_doc()
    days = doc["days"]
    reasons = doc.get("reasons", [])
    validate(days)
    pf = preflight()
    stats = pipeline_stats()
    gate = "under" if stats["ready"] < 5 else "AT OR OVER"
    rendered = "\n\n".join(
        render_day(d, i == 0, pf) for i, d in enumerate(days)
    )
    archive = (
        ""
        if len(days) > 1
        else '\n<p class="dl-archive-empty">No earlier days yet — this is day one of the log.</p>'
    )
    reason_options = "\n      ".join(
        f'<label class="dl-reason"><input type="checkbox" value="{r["key"]}"'
        f' data-revivable="{str(bool(r.get("revivable"))).lower()}" />'
        f'<span>{r["label"]}</span>'
        f'<span class="dl-revive {"yes" if r.get("revivable") else "no"}">'
        f'{"can come back" if r.get("revivable") else "closed for good"}</span></label>'
        for r in reasons
    )
    reasons_json = json.dumps(reasons)
    OUT.write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Daily to-do — full-time JD workspace (v2)</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
<main class="page" id="main">

<p class="breadcrumb"><a href="../index.html">Full-time JD workspace</a> · daily log</p>

<p class="dl-store" id="store-banner" hidden></p>

<header>
  <p class="eyebrow">Individual-contributor (IC) roles · Principal / Staff / Architect</p>
  <h1>Daily to-do</h1>
</header>

<div class="tldr">
  <strong>Where things stand</strong>
  <strong>{stats['total']}</strong> job workspaces built · <strong>{stats['sent']}</strong> sent ·
  ready-and-unsent backlog <strong>{stats['ready']}</strong>, {gate} the roughly-five gate.
  Sending is the north star, not building. Anything left unticked rolls over to the next day
  automatically. <span class="dim">Generated from <code>daily/days.json</code>; counts read from
  the root launcher on each render.</span>
</div>

{rendered}

<h2>Earlier days</h2>{archive}

<dialog id="move-dialog" class="dl-dialog">
  <form>
    <h3 id="move-title">Move out</h3>
    <p class="dl-dialog-task" id="move-task"></p>
    <fieldset class="dl-field dl-reasons" id="move-reasons">
      <legend>Reasons — pick at least one</legend>
      {reason_options}
    </fieldset>
    <p class="dl-reason-hint" id="move-hint" hidden>Pick at least one reason.</p>
    <label class="dl-field" id="move-until-field" hidden>Comes back on
      <input type="date" id="move-until" />
    </label>
    <label class="dl-field">Note <span class="dim">(optional)</span>
      <textarea id="move-note" rows="2" placeholder="what changed"></textarea>
    </label>
    <p class="dl-dialog-actions">
      <button type="button" class="dl-act" id="move-cancel">Cancel</button>
      <button type="button" class="dl-act primary" id="move-confirm">Move out</button>
    </p>
  </form>
</dialog>

</main>
<script type="application/json" id="reasons">{reasons_json}</script>
<script src="../static/todo.js" defer></script>
</body>
</html>
""")
    total = sum(len(g["items"]) for d in days for g in d["groups"])
    print(f"[daily] wrote {OUT.relative_to(ROOT)} — {len(days)} day(s), {total} task(s)")
    print(f"[daily] pipeline: {stats}  pre-flight ok={pf.get('ok')}")


if __name__ == "__main__":
    main()
