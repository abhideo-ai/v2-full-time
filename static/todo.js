// Daily log: a Kanban whose lanes ARE the state machine in automation/db.py.
//
// State lives in PostgreSQL behind automation/serve.py. The page sends
// OPERATIONS ("done", "undone", "parked", "pushed", "dropped", "restored"),
// never a state blob, so the server can append each one to history and fold it
// into current state in one transaction.
//
// LANES ≡ OPS. Open · Done · Parked · Pushed · Dropped, and nothing else.
// db.ACTIONS has no "in progress", so a lane for it would write a state ./todo
// could never read back; the drop handler is therefore a lookup rather than a
// translation layer, and a drag produces the same task_event row as
// `./todo park <id> --reason blocked`.
//
// TWO RULES THIS FILE EXISTS TO PROTECT:
//
//   1. A DROP IS A REQUEST, NEVER A COMMIT. Dropping a card on Parked, Pushed
//      or Dropped opens the reason dialog and writes NOTHING. The card does not
//      move in the meantime — an optimistic move would put a reasonless park on
//      screen, which is the one thing that must never ship. The database
//      refuses it too (db.validate, plus two CHECKs), so this is the outermost
//      of three independent refusals, not the only one.
//   2. WAITING IS A SORT, NEVER A LOCK. A task whose prerequisites are unticked
//      sorts below the ready ones inside Open and is badged, but it is never
//      greyed out, never disabled, and never moved to a lane of its own —
//      doing things out of order is legitimate.
//
// Against a plain `python3 -m http.server` there is no API, so the page falls
// back to localStorage and says so in the banner. applyLocal() below mirrors
// the server's transition table exactly, so both modes behave identically.
//
// Everything date-related is computed HERE, from the browser's clock. That is
// what dates the board TODAY rather than "the newest day in days.json" — two
// different dates whenever nothing was authored for today — and what makes
// refreshing a pinned tab worth doing: a task pushed to Thursday returns on
// Thursday without anyone regenerating the page.
document.addEventListener("DOMContentLoaded", async () => {
  const LS_KEY = "v2-daily-todo";
  // NOT toISOString(): that is UTC, and east of Greenwich it reports tomorrow
  // for the first hours of the day — on a page whose whole job is "what is due
  // today", that is the one bug that must not exist.
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const TODAY = iso(new Date());
  const daysBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);
  const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  // Same shape as daily.py's strftime, so the board header and a day heading
  // cannot read differently for the same date.
  const pretty = s => {
    const d = new Date(`${s}T00:00:00`);
    return `${WD[d.getDay()]} ${d.getDate()} ${MO[d.getMonth()]} ${d.getFullYear()}`;
  };
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

  // Captured before anything mutates it: the generated <title> is the fallback
  // for a no-JS view, and the stem every live title is built on.
  const BASE_TITLE = document.title;
  const dayEls = [...document.querySelectorAll(".dl-day")];
  const board = document.getElementById("board");
  const banner = document.getElementById("store-banner");
  const nextEl = document.getElementById("next-up");
  const nextText = nextEl && nextEl.querySelector("p:last-child");
  const sayEl = document.getElementById("kb-say");
  const entries = [];
  const byLi = new Map();
  let store = "local";
  const REASONS = (() => {
    try { return JSON.parse(document.getElementById("reasons").textContent); }
    catch { return []; }
  })();
  const labelOf = k => (REASONS.find(r => r.key === k) || {}).label || k;
  // A task can come back only if EVERY reason it carries is revivable — one
  // terminal reason (the posting is gone) closes it regardless of the others.
  const canComeBack = rs =>
    Array.isArray(rs) && rs.length > 0 &&
    rs.every(k => (REASONS.find(r => r.key === k) || { revivable: true }).revivable);
  let state = {};

  // ---- lanes --------------------------------------------------------------
  // DOM order and keyboard order. Every name after "open" is verbatim a
  // db.ACTIONS value; "open" is the lane you come back to, reached by
  // "restored" or "undone" depending on where the card is.
  const LANES = ["open", "done", "parked", "pushed", "dropped"];
  const OUT_LANES = new Set(["parked", "pushed", "dropped"]);
  const LANE_NAME = {
    open: "open", done: "done", parked: "parked",
    pushed: "pushed to a later day", dropped: "dropped",
  };

  // Placement is a pure function of ONE task_state row plus the clock. Nothing
  // is stored that db.py does not already store.
  //
  // `moved` outranks `done`, because _SET["parked"] does not clear `done`: tick
  // then park is reachable and belongs in Parked. _SET["done"] DOES clear the
  // move, so the reverse — park then tick — lands in Done, correctly.
  const laneOf = s => {
    if (s.moved === "parked") return "parked";
    if (s.moved === "dropped") return "dropped";
    // Pushed is a TIMED lane: it empties itself when the return date arrives,
    // with no write and nobody regenerating the page.
    if (s.moved === "pushed") return s.until && s.until > TODAY ? "pushed" : "open";
    return s.done === true ? "done" : "open";
  };
  const isOut = s => OUT_LANES.has(laneOf(s));

  const zones = new Map(
    [...document.querySelectorAll(".kb-drop")].map(z => [z.dataset.drop, z]));

  const say = msg => {
    if (!sayEl) return;
    sayEl.textContent = msg;
    sayEl.hidden = !msg;
  };

  // ---- backend ------------------------------------------------------------
  const setBanner = (text, kind) => {
    if (!banner) return;
    banner.textContent = text;
    banner.className = `dl-store ${kind}`;
    banner.hidden = false;
  };

  const probe = async () => {
    try {
      const r = await fetch("/__daily_api", { cache: "no-store" });
      if (r.ok && (await r.json()).ok) return "postgresql";
    } catch { /* plain static server */ }
    return "local";
  };

  const loadState = async () => {
    if (store === "postgresql") {
      try {
        const r = await fetch("/api/state", { cache: "no-store" });
        if (r.ok) return (await r.json()).tasks || {};
      } catch { /* fall through */ }
    }
    try { return JSON.parse(localStorage.getItem(LS_KEY) || "{}"); } catch { return {}; }
  };

  // Mirrors _SET in automation/db.py. Keep the two in step. Note `reasons`,
  // plural and an array: the op carries a list, every reader wants a list, and
  // storing a singular `reason` here made every locally-parked task render
  // "closed for good" with no reasons shown.
  const applyLocal = op => {
    const t = state[op.key] || (state[op.key] = { done: false });
    const clearMove = () => {
      delete t.moved; delete t.reasons; delete t.note; delete t.until; delete t.moved_at;
    };
    if (op.action === "done") { t.done = true; t.done_at = new Date().toISOString(); clearMove(); }
    else if (op.action === "undone") { t.done = false; delete t.done_at; }
    else if (op.action === "restored") { clearMove(); }
    else {
      t.moved = op.action;
      t.reasons = op.reasons;
      t.note = op.note;
      t.until = op.until;
      t.moved_at = new Date().toISOString();
    }
  };

  const sendOp = async op => {
    if (store === "postgresql") {
      try {
        const r = await fetch("/api/ops", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ops: [op] }),
        });
        const payload = await r.json().catch(() => ({}));
        if (r.ok) { state = payload.tasks || {}; return true; }
        setBanner(`Not saved — ${payload.error || r.status}`, "bad");
        return false;
      } catch (e) {
        setBanner(`Not saved — server unreachable (${e.message})`, "bad");
        return false;
      }
    }
    applyLocal(op);
    try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch { /* quota/private */ }
    return true;
  };

  const act = async op => { if (await sendOp(op)) render(); };

  // ---- registry -----------------------------------------------------------
  const st = key => state[key] || {};
  let dragging = null;

  const register = li => {
    const box = li.querySelector('input[type="checkbox"]');
    if (!box) return;
    const dayId = li.dataset.day || (li.closest(".dl-day") || {}).dataset.day;
    const e = {
      li, box, dayId,
      id: li.dataset.id,
      // The key keeps its ORIGIN day. Re-keying a rolled task to today would
      // fork its history in two and break task_state_key_shape.
      key: `${dayId}::${li.dataset.id}`,
      p: Number(li.dataset.p) || 2,
      ord: Number(li.dataset.ord) || 0,
      gidx: li.dataset.group || "0",
      due: li.dataset.due || dayId,
      needs: (li.dataset.needs || "").split(",").filter(Boolean),
      onBoard: false, rolled: false, wait: 0,
    };
    entries.push(e);
    byLi.set(li, e);
    box.addEventListener("change", () =>
      act({ key: e.key, action: box.checked ? "done" : "undone" }));
    li.querySelectorAll(".dl-act").forEach(btn =>
      btn.addEventListener("click", ev => {
        ev.preventDefault();
        const action = btn.dataset.act;
        if (action === "restored") act({ key: e.key, action });
        else openDialog(e, action);
      }));

    // Drag, and its keyboard twin. Both funnel into dropOn(), so they cannot
    // drift apart and the reason rule is enforced once, not twice.
    const grab = li.querySelector(".kb-grab");
    if (grab) {
      // draggable is set only while the handle is held: a permanently draggable
      // <li> makes the detail text — which IS the instruction on most of these
      // tasks — impossible to select and copy.
      grab.addEventListener("pointerdown", () => { li.draggable = true; });
      grab.addEventListener("keydown", ev => {
        const i = LANES.indexOf(laneOf(st(e.key)));
        const to = ev.key === "ArrowRight" ? LANES[i + 1]
                 : ev.key === "ArrowLeft" ? LANES[i - 1] : null;
        if (!to) return;
        ev.preventDefault();
        dropOn(e, to);
      });
      grab.addEventListener("focus", () =>
        say("Left and right arrows move this card between lanes."));
    }
    li.addEventListener("dragstart", ev => {
      dragging = e;
      li.classList.add("kb-dragging");
      if (ev.dataTransfer) {
        ev.dataTransfer.effectAllowed = "move";
        try { ev.dataTransfer.setData("text/plain", e.key); } catch { /* jsdom */ }
      }
    });
    li.addEventListener("dragend", () => {
      dragging = null;
      li.draggable = false;
      li.classList.remove("kb-dragging");
      zones.forEach(z => z.classList.remove("kb-over"));
    });
    return e;
  };

  document.querySelectorAll(".dl-day .dl-list > li").forEach(register);

  zones.forEach((zone, lane) => {
    zone.addEventListener("dragover", ev => {
      if (!dragging) return;
      ev.preventDefault();
      zone.classList.add("kb-over");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("kb-over"));
    zone.addEventListener("drop", ev => {
      if (ev.preventDefault) ev.preventDefault();
      zone.classList.remove("kb-over");
      const e = dragging;
      dragging = null;
      if (e) dropOn(e, lane);
    });
  });

  // ONE routing table for every gesture: mouse drag, arrow key, or the buttons
  // on the card. A move-out lane never writes here — it asks.
  function dropOn(e, lane) {
    const s = st(e.key);
    const from = laneOf(s);
    if (lane === from) return say(`Already ${LANE_NAME[lane]}.`);
    if (lane === "open") {
      say(s.moved ? "Restored." : "Unticked.");
      return act({ key: e.key, action: s.moved ? "restored" : "undone" });
    }
    if (lane === "done") {
      say("Ticked.");
      return act({ key: e.key, action: "done" });
    }
    // parked / pushed / dropped — the reason gate. Nothing is written, and the
    // card stays where it is, until a reason is picked.
    return openDialog(e, lane);
  }

  // ---- move-out dialog ----------------------------------------------------
  const dlg = document.getElementById("move-dialog");
  const TITLES = { parked: "Park this task", pushed: "Push to a later day", dropped: "Drop this task" };
  let pending = null;

  function openDialog(entry, action) {
    if (!dlg) return;
    pending = { entry, action };
    document.getElementById("move-title").textContent = TITLES[action];
    document.getElementById("move-task").innerHTML = entry.li.querySelector(".dl-task").innerHTML;
    document.getElementById("move-confirm").textContent =
      action === "pushed" ? "Push" : action === "dropped" ? "Drop" : "Park";
    const untilField = document.getElementById("move-until-field");
    const until = document.getElementById("move-until");
    untilField.hidden = action !== "pushed";
    const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
    until.value = iso(tomorrow);
    until.min = iso(new Date());
    document.getElementById("move-note").value = "";
    document.getElementById("move-hint").hidden = true;
    dlg.querySelectorAll("#move-reasons input").forEach(c => { c.checked = false; });
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  }

  const closeDialog = () => {
    // Bind the buttons directly rather than leaning on <form method="dialog">
    // and returnValue: that path is the fiddliest corner of the dialog API and
    // the first thing to behave differently between engines.
    if (dlg.close) dlg.close(); else dlg.removeAttribute("open");
  };

  if (dlg) {
    document.getElementById("move-cancel").addEventListener("click", () => {
      pending = null;
      closeDialog();
      say("Nothing moved — no reason given.");
    });
    document.getElementById("move-confirm").addEventListener("click", async () => {
      const reasons = [...dlg.querySelectorAll("#move-reasons input:checked")].map(c => c.value);
      if (!reasons.length) {
        // Do NOT close: moving a task out without saying why is the one thing
        // this dialog exists to prevent, and the database refuses it anyway.
        document.getElementById("move-hint").hidden = false;
        return;
      }
      const p = pending; pending = null;
      closeDialog();
      if (!p) return;
      const op = {
        key: p.entry.key,
        action: p.action,
        reasons,
        note: document.getElementById("move-note").value.trim() || null,
      };
      if (p.action === "pushed") op.until = document.getElementById("move-until").value;
      await act(op);
      say(`Moved to ${LANE_NAME[p.action]}.`);
    });
  }

  // ---- render -------------------------------------------------------------
  const dueBadge = e => {
    const s = st(e.key);
    // isOut(s), not isOut(e): the entry has no `moved`, so passing it here left
    // every parked card still advertising "3 days overdue".
    if (s.done || isOut(s)) return null;
    const due = s.moved === "pushed" && s.until ? s.until : e.due;
    if (due < TODAY) {
      const n = daysBetween(due, TODAY);
      return { cls: "red", text: n === 1 ? "1 day overdue" : `${n} days overdue` };
    }
    if (due === TODAY) return { cls: "yellow", text: "due today" };
    return { cls: "fact", text: `due ${due}` };
  };

  function relocate(e) {
    // Cards that did not make it onto the board stay in their day's list. They
    // are still live — tick one, or use its buttons — they simply do not
    // pretend to be today's work.
    if (!e.onBoard) return;
    const zone = zones.get(laneOf(st(e.key)));
    if (zone && e.li.parentNode !== zone) zone.appendChild(e.li);
  }

  // Ready before waiting, then priority — byte-for-byte the order "Do next"
  // already picked from, so the top card of Open IS the pick.
  const ORDER = {
    open: (a, b) => a.wait - b.wait || a.p - b.p || Number(b.rolled) - Number(a.rolled)
                    || cmp(a.dayId, b.dayId) || a.ord - b.ord,
    done: (a, b) => cmp(st(b.key).done_at || "", st(a.key).done_at || "") || a.ord - b.ord,
    out: (a, b) => Number(canComeBack(st(b.key).reasons)) - Number(canComeBack(st(a.key).reasons))
                   || cmp(st(b.key).moved_at || "", st(a.key).moved_at || "") || a.ord - b.ord,
  };

  function sortLanes() {
    zones.forEach((zone, lane) => {
      const by = ORDER[lane] || ORDER.out;
      const kids = [...zone.children].filter(n => byLi.has(n));
      kids.sort((x, y) => by(byLi.get(x), byLi.get(y)));
      kids.forEach(n => zone.appendChild(n));
    });
  }

  function badge(e, cls, text, sel) {
    const meta = e.li.querySelector(".dl-meta");
    if (!meta) return;
    let el = meta.querySelector(sel);
    if (!text) { if (el) el.remove(); return; }
    if (!el) {
      el = document.createElement("span");
      el.className = sel.slice(1);
      meta.appendChild(el);
    }
    el.textContent = text;
    el.dataset.tone = cls;
  }

  function counts() {
    // Re-derived from the rows actually in the DOM, on EVERY render — the
    // launcher's lesson: counting once at boot showed 0 above a full list.
    document.querySelectorAll(".kb-zone").forEach(z => {
      const n = z.querySelectorAll(".dl-list > li").length;
      z.querySelector(".n").textContent = n;
      // Deliberately NOT hidden when empty: a zone you cannot see is a zone you
      // cannot drop onto.
      z.classList.toggle("empty", n === 0);
    });
    document.querySelectorAll(".kb-lane").forEach(l => {
      const n = l.querySelectorAll(".kb-drop > li").length;
      const el = l.querySelector(".kb-n");
      if (el) el.textContent = n;
      const empty = l.querySelector(".kb-empty");
      if (empty) empty.hidden = n > 0;
    });
  }

  function render() {
    entries.forEach(e => {
      const s = st(e.key);
      const done = s.done === true;
      e.box.checked = done;
      e.li.classList.toggle("done", done);

      // Blockers resolve against the card's OWN day, not today — a rolled task
      // depends on what it depended on when it was written.
      const blockers = e.needs.filter(n => st(`${e.dayId}::${n}`).done !== true);
      const waiting = !done && !isOut(s) && blockers.length > 0;
      e.wait = waiting ? 1 : 0;
      e.li.classList.toggle("waiting", waiting);
      badge(e, "warn", waiting
        ? (blockers.length === 1 ? "waiting on 1 task" : `waiting on ${blockers.length} tasks`)
        : null, ".dl-waiting");

      const d = dueBadge(e);
      badge(e, d ? d.cls : "", d ? d.text : null, ".dl-due");

      e.li.classList.toggle("moved", !!s.moved);
      const why = [(s.reasons || []).map(labelOf).join(" + "), s.note]
        .filter(Boolean).join(" — ");
      badge(e, "muted", s.moved
        ? `${s.moved}${s.until ? ` until ${s.until}` : ""}${why ? ` · ${why}` : ""}`
        : null, ".dl-movednote");
      const revive = s.moved ? canComeBack(s.reasons) : null;
      badge(e, revive ? "good" : "muted",
        s.moved ? (revive ? "can come back" : "closed for good") : null, ".dl-revivable");
      e.li.classList.toggle("closed-for-good", s.moved && revive === false);
      e.li.querySelectorAll(".dl-act").forEach(b => {
        b.hidden = (b.dataset.act === "restored") !== !!s.moved;
      });

      relocate(e);
    });

    sortLanes();
    counts();

    dayEls.forEach(day => {
      const id = day.dataset.day;
      const count = day.querySelector(".dl-count");
      const mine = entries.filter(e => e.dayId === id && !isOut(st(e.key)));
      if (count) {
        if (!mine.length) { count.textContent = ""; }
        else {
          const done = mine.filter(e => st(e.key).done === true).length;
          count.textContent = `${done}/${mine.length} done`;
          count.classList.toggle("all-done", done === mine.length);
        }
      }
      const onboard = day.querySelector(".dl-onboard");
      if (onboard) {
        const n = entries.filter(e => e.dayId === id && e.onBoard).length;
        onboard.textContent = n ? `${n} on the board` : "";
      }
    });

    const mine = entries.filter(e => e.onBoard && !isOut(st(e.key)));
    const open = mine.filter(e => st(e.key).done !== true);

    // Live tab title. A pinned tab should say where things stand without being
    // opened, so the numbers lead — a tab strip truncates the tail, never the head.
    const overdue = open.filter(e => {
      const s2 = st(e.key);
      const due = s2.moved === "pushed" && s2.until ? s2.until : e.due;
      return due < TODAY;
    }).length;
    const bits = [];
    if (overdue) bits.push(`${overdue} overdue`);
    if (mine.length) bits.push(open.length ? `${mine.length - open.length}/${mine.length}` : "✓ all done");
    document.title = bits.length ? `${bits.join(" · ")} · ${BASE_TITLE}` : BASE_TITLE;

    if (!nextText) return;
    entries.forEach(e => e.li.classList.remove("kb-next"));
    // The Open lane is already sorted ready-first, so this is its top card.
    const ready = open.filter(e => e.wait === 0).sort(ORDER.open);
    nextEl.hidden = false;
    if (ready.length) {
      const pick = ready[0];
      pick.li.classList.add("kb-next");
      nextText.innerHTML =
        `<span class="pill ${["", "red", "yellow", "fact"][pick.p]}">P${pick.p}</span> ` +
        pick.li.querySelector(".dl-task").innerHTML +
        (pick.rolled ? ` <span class="dl-from">rolled over from ${pick.dayId}</span>` : "");
    } else if (!open.length) {
      nextText.textContent = mine.length
        ? "Everything on today's board is ticked."
        : "Nothing on today's board.";
    } else {
      nextText.textContent =
        `Nothing is unblocked — all ${open.length} remaining tasks are waiting on something else.`;
    }
  }

  // ---- boot ---------------------------------------------------------------
  store = await probe();
  state = await loadState();
  setBanner(
    store === "postgresql"
      ? "Saving to PostgreSQL (v2_daily) — state survives refreshes, browsers and cleared site data."
      : "Not saving to disk. Start automation/serve.py to save to PostgreSQL; until then state stays in this browser only.",
    store === "postgresql" ? "ok" : "warn",
  );

  // The board is dated from the CLOCK, never from days.json. The generator
  // writes today's date as a no-JS fallback; this is what keeps a pinned tab
  // honest after midnight.
  if (board) {
    board.dataset.day = TODAY;
    const h = document.getElementById("board-date");
    if (h) h.textContent = pretty(TODAY);
  }

  // Board membership, decided ONCE, here: today's tasks, plus everything from
  // an earlier day that is neither done nor moved out. That is rollover — and
  // it is a MOVE, not a clone, so one task is one node and the whole class of
  // bug where two nodes disagree about one database row cannot happen.
  entries.forEach(e => {
    const s = st(e.key);
    e.onBoard = e.dayId === TODAY || (e.dayId < TODAY && s.done !== true && !s.moved);
    e.rolled = e.onBoard && e.dayId !== TODAY;
    if (e.rolled) {
      const meta = e.li.querySelector(".dl-meta");
      if (meta && !meta.querySelector(".dl-from")) {
        meta.insertAdjacentHTML("beforeend", `<span class="dl-from">from ${e.dayId}</span>`);
      }
    }
  });

  // Authored context keeps a home: a chip is not a substitute for the paragraph
  // saying why a group of tasks exists. Only strips with cards on the board show.
  document.querySelectorAll(".kb-ctx").forEach(ctx => {
    ctx.hidden = !entries.some(e =>
      e.onBoard && e.dayId === ctx.dataset.day && e.gidx === ctx.dataset.group);
  });

  const note = document.getElementById("board-rolled");
  if (note) {
    const rolled = entries.filter(e => e.rolled).length;
    const authored = dayEls.some(d => d.dataset.day === TODAY);
    note.textContent = !authored && rolled
      ? `Nothing was authored for today — all ${rolled} card${rolled === 1 ? "" : "s"} rolled over.`
      : rolled
        ? `${rolled} card${rolled === 1 ? "" : "s"} rolled over from an earlier day.`
        : "";
    note.hidden = !note.textContent;
  }

  render();
});
