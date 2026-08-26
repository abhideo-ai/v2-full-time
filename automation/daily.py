#!/usr/bin/env python3
"""Render daily/index.html from daily/days.json.

    automation/.venv/bin/python automation/daily.py

The log is regenerated every day, so the HTML is derived, never authored by
hand: editing days.json is the whole workflow and this file owns the markup.

Two header facts are derived from the repo on every run, so they cannot drift:
the pipeline counts (read from the root launcher's data-status rows) and the
parser pre-flight (the real upgrad_resume_paste parser, run against master/).

`task`, `detail` and `why` are TRUSTED HTML and are deliberately not escaped.

THE BOARD IS THE PAGE; days.json IS ITS SOURCE.
-----------------------------------------------
The page renders as a Kanban whose lanes are the state machine that already
exists in automation/db.py — Open · Done · Parked · Pushed · Dropped. There is
deliberately no "In progress": db.ACTIONS has no such action, so a lane for it
would write a state ./todo could never read back. Lanes ≡ ops means a drop and
`./todo park <id> --reason blocked` produce byte-identical task_event rows.

The board is dated TODAY, not "the newest day in days.json". Those are different
dates whenever nothing was authored for today, and the whole job of this page is
to answer "what is due today". The date below is a no-JS fallback only —
static/todo.js recomputes it from the browser clock at boot, so a pinned tab is
right after midnight without anyone regenerating anything.

ROLLOVER IS NOT DONE HERE, and it no longer clones. Tick state lives in
PostgreSQL, which Python cannot see, so static/todo.js decides at load time
which cards belong on the board and MOVES them there — one <li> per task, ever.
days.json never duplicates a task. Each day's list below the board is where its
cards came from, and stays the provenance record.
"""
import html as html_mod
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

# The board's lanes, in DOM order. Each `drop` value is EXACTLY an action name
# from db.ACTIONS (or "open", the lane you come back to), so the drop handler is
# a lookup, not a translation layer. Add a lane here only if db.py grew a state.
OUT_ZONES = (
    ("parked", "park", "Parked", "Set aside. It comes back only if every reason it carries can."),
    ("pushed", "push", "Pushed to a later day", "Returns on its own date — nothing to remember."),
    ("dropped", "drop", "Dropped", "Closed out. Still here, still restorable if its reasons allow."),
)


def plain(markup: str) -> str:
    """Task text is authored as HTML; an aria-label wants none of it."""
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", "", markup))).strip()


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
    """Counts from `jobs_tracker_v2`, which IS the pipeline's record.

    This used to scrape `data-status` attributes out of the root launcher's
    `#app-list`. That div has been empty markup ever since the launcher started
    rendering from `GET /api/jobs` — CLAUDE.md's "never hand-write a row into
    #app-list" is the same rule seen from the other side — so the scrape matched
    ZERO rows and this page reported `0 built · 0 sent · backlog 0` above a
    database holding four live seats.

    The backlog gate is the one number on this page that decides anything.
    Reporting it as a confident 0 is worse than not reporting it, so an
    unreachable database says so instead of counting to zero.
    """
    try:
        import jobs_db
        rows = jobs_db.applications()
    except Exception as exc:                                    # noqa: BLE001
        return {"ok": False, "why": f"{type(exc).__name__}: {exc}".split("\n")[0]}
    return {
        "ok": True,
        "total": len(rows),
        "ready": sum(1 for r in rows if r["tab"] == "ready"),
        "sent": sum(1 for r in rows if r["status"] in jobs_db.SENT_STATUSES),
    }


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


def render_item(item: dict, day: str, gidx: int, ord_: int) -> str:
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
    # The detail IS the instruction on most of these tasks, so it is never
    # collapsed behind a disclosure: a board you have to click through to read
    # is worse than the list it replaced.
    label = html_mod.escape(plain(item["task"])[:110], quote=True)
    return f"""        <li data-id="{item['id']}" data-day="{day}" data-group="{gidx}" data-ord="{ord_}" data-needs="{','.join(needs)}" data-p="{prio}" data-due="{due}">
          <button type="button" class="kb-grab" aria-label="Move &lsquo;{label}&rsquo; to another lane" aria-keyshortcuts="ArrowLeft ArrowRight" aria-describedby="kb-help">&#x283F;</button>
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


def render_group(group: dict, day: str, gidx: int) -> str:
    kind = f" {group['kind']}" if group.get("kind") else ""
    why = f'      <p class="dl-why">{group["why"]}</p>\n' if group.get("why") else ""
    items = "\n".join(
        render_item(i, day, gidx, n) for n, i in enumerate(group["items"])
    )
    return f"""    <div class="dl-group{kind}" data-group="{gidx}">
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
            '<div class="callout bad">\n'
            "  <b>Pre-flight FAILED.</b> The parser could not read "
            "<code>master/upgrad_resume.html</code> cleanly, so an export would ship whatever "
            f"it managed to parse: {pf.get('why', '')} "
            f"ids={pf.get('ids', '?')}/10, "
            f"<code>[fill in metric]</code>×{pf.get('placeholders', '?')}. Fix this before "
            "exporting anything.\n</div>"
        )
    return (
        '<div class="callout good">\n'
        "  <b>Pre-flight green — no action needed.</b> Checked on this render, not quoted "
        f"from memory: all <strong>{pf['ids']}</strong> <code>quick-*</code> ids present in "
        "<code>master/upgrad_resume.html</code>, all parse with no silent skip, skills "
        f"{' · '.join(str(c) for c in pf['skills'])} and experience "
        f"{' · '.join(str(c) for c in pf['exp'])} = <strong>{pf['bullets']}</strong> bullets, "
        "zero <code>[fill in metric]</code>. Nothing in the HTML is blocking an export — only "
        "the card is.\n</div>"
    )


def render_context(days: list[dict]) -> str:
    """Why each group of tasks exists. Authored prose, so it keeps a home.

    A board reduces a group to a chip, and the chip is not a substitute for the
    paragraph. These strips sit above the lanes and static/todo.js shows only
    the ones whose tasks actually made it onto the board.
    """
    strips = []
    for day in days:
        for gidx, group in enumerate(day["groups"]):
            kind = f" {group['kind']}" if group.get("kind") else ""
            why = f'\n        <p class="dl-why">{group["why"]}</p>' if group.get("why") else ""
            strips.append(
                f'      <div class="kb-ctx{kind}" data-day="{day["date"]}" '
                f'data-group="{gidx}" hidden>\n'
                f'        <h3>{group["title"]}</h3>{why}\n'
                f"      </div>"
            )
    return "\n".join(strips)


def render_board(days: list[dict]) -> str:
    """The Kanban. Lanes are db.py's states; nothing here invents one."""
    today = date.today()
    pretty = today.strftime("%a %d %b %Y").replace(" 0", " ")
    zones = "\n".join(
        f'        <details class="kb-zone" id="moved-{key}" data-zone="{key}" open>\n'
        f'          <summary>{title} <span class="n">0</span></summary>\n'
        f'          <p class="kb-zone-why">{why}</p>\n'
        f'          <ul class="dl-list kb-drop" data-drop="{key}" '
        f'aria-label="{title} — drop a card here to {verb} it, with a reason"></ul>\n'
        f"        </details>"
        for key, verb, title, why in OUT_ZONES
    )
    return f"""<section class="kb" id="board" data-day="{today.isoformat()}" aria-labelledby="board-date">
  <div class="kb-head">
    <h2 id="board-date">{pretty}</h2>
    <p class="kb-rolled" id="board-rolled" hidden></p>
  </div>
  <p class="kb-help" id="kb-help">Drag a card by its <span aria-hidden="true">&#x283F;</span> handle,
    or focus the handle and press <kbd>&larr;</kbd> / <kbd>&rarr;</kbd> — the same move, same code
    path. Every card also carries Park / Push / Drop buttons that do exactly the same thing.
    <strong>Nothing leaves the board until you have given at least one reason</strong>: a drop is a
    request, never a save.</p>
  <p class="kb-say" id="kb-say" role="status" aria-live="polite" hidden></p>

  <div class="wl-donow" id="next-up" hidden>
    <p class="lbl">Do next</p>
    <p></p>
  </div>

  <div class="kb-context" id="board-context">
{render_context(days)}
  </div>

  <div class="kb-lanes">
    <section class="kb-lane" id="lane-open" aria-labelledby="lane-open-h">
      <h3 id="lane-open-h">Open <span class="kb-n">0</span></h3>
      <p class="kb-lane-why">Ready first, then anything still waiting on a prerequisite —
        <strong>waiting is a sort, never a lock</strong>. Doing things out of order is legitimate.</p>
      <ul class="dl-list kb-drop" data-drop="open" aria-label="Open — drop a card here to bring it back"></ul>
      <p class="kb-empty">Nothing open.</p>
    </section>

    <section class="kb-lane" id="lane-done" aria-labelledby="lane-done-h">
      <h3 id="lane-done-h">Done <span class="kb-n">0</span></h3>
      <p class="kb-lane-why">Ticked. Drop one back on Open to untick it.</p>
      <ul class="dl-list kb-drop" data-drop="done" aria-label="Done — drop a card here to tick it"></ul>
      <p class="kb-empty">Nothing ticked yet.</p>
    </section>

    <section class="kb-lane kb-lane-out" id="lane-out" aria-labelledby="lane-out-h">
      <h3 id="lane-out-h">Moved out <span class="kb-n">0</span></h3>
      <p class="kb-lane-why">Three zones, three reasons-required moves. Each one asks before it
        writes.</p>
{zones}
    </section>
  </div>
</section>"""


def render_day(day: dict, is_today: bool) -> str:
    pretty = date.fromisoformat(day["date"]).strftime("%a %d %b %Y").replace(" 0", " ")
    classes = "dl-day today" if is_today else "dl-day"
    today_pill = ' <span class="pill note">today</span>' if is_today else ""
    blocks = [render_group(g, day["date"], n) for n, g in enumerate(day["groups"])]
    blocks += [render_callout(c) for c in day.get("callouts", [])]
    body = "\n\n".join(blocks)
    return f"""<details class="{classes}" data-day="{day['date']}"{' open' if is_today else ''}>
  <summary>{pretty}{today_pill}<span class="dl-count"></span><span class="dl-onboard"></span></summary>
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
    today = date.today().isoformat()
    if stats["ok"]:
        gate = "under" if stats["ready"] < 5 else "AT OR OVER"
        standing = (
            f"<strong>{stats['total']}</strong> job workspaces built · "
            f"<strong>{stats['sent']}</strong> sent · ready-and-unsent backlog "
            f"<strong>{stats['ready']}</strong>, {gate} the roughly-five gate."
        )
        source = "counts read from <code>jobs_tracker_v2</code> on each render"
    else:
        standing = (
            "Pipeline counts unavailable — <code>jobs_tracker_v2</code> could not be read on "
            f"this render ({stats['why']}). The backlog gate is left unsaid rather than "
            "reported as zero."
        )
        source = "pipeline counts come from <code>jobs_tracker_v2</code>"
    rendered = "\n\n".join(render_day(d, d["date"] == today) for d in days)
    archive = (
        ""
        if len(days) > 1
        else '\n<p class="dl-archive-empty">One day on file so far — every card on the board '
             "above came from it.</p>"
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
  <title>Daily to-do</title>
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

<div class="tldr" id="standing">
  <strong>Where things stand</strong>
  {standing}
  Sending is the north star, not building. Anything left unticked rolls over to the next day
  automatically. <span class="dim">Generated from <code>daily/days.json</code>; {source}.</span>
</div>

{preflight_callout(pf)}

{render_board(days)}

<h2>Where each card came from</h2>
<p class="dl-archive-note">Every task exactly as authored in <code>daily/days.json</code>, by the
day it was written for. Cards on the board above were <em>moved</em> out of these lists, never
copied — one task is one row in the database and one node in the page.</p>{archive}

{rendered}

<dialog id="move-dialog" class="dl-dialog">
  <form>
    <h3 id="move-title">Move out</h3>
    <p class="dl-dialog-task" id="move-task"></p>
    <fieldset class="dl-field dl-reasons" id="move-reasons">
      <legend>Reasons — pick at least one</legend>
      {reason_options}
    </fieldset>
    <p class="dl-reason-hint" id="move-hint" role="alert" hidden>Pick at least one reason.</p>
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
    authored_today = any(d["date"] == today for d in days)
    print(f"[daily] wrote {OUT.relative_to(ROOT)} — {len(days)} day(s), {total} task(s)")
    print(f"[daily] board dated {today}"
          f"{'' if authored_today else ' (nothing authored for today — rolled cards only)'}")
    print(f"[daily] pipeline: {stats}  pre-flight ok={pf.get('ok')}")
    if not stats["ok"]:
        print("[daily] WARNING: pipeline counts unavailable — the page says so "
              "rather than reporting a backlog of zero")


if __name__ == "__main__":
    main()
