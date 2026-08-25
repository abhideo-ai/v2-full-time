// Daily log: state, priorities, dependencies, rollover and move-out.
//
// State lives in PostgreSQL behind automation/serve.py. The page sends
// OPERATIONS ("done", "parked", "pushed", "dropped", "restored"), never a state
// blob, so the server can append each one to history and fold it into current
// state in one transaction.
//
// Against a plain `python3 -m http.server` there is no API, so the page falls
// back to localStorage and says so in the banner. applyLocal() below mirrors
// the server's transition table exactly, so both modes behave identically.
//
// Everything date-related is computed HERE, from the browser's clock, which is
// what makes refreshing a pinned tab worth doing: a task pushed to Thursday
// returns on Thursday without anyone regenerating the page.
document.addEventListener("DOMContentLoaded", async () => {
  const LS_KEY = "v2-daily-todo";
  // NOT toISOString(): that is UTC, and east of Greenwich it reports tomorrow
  // for the first hours of the day — on a page whose whole job is "what is due
  // today", that is the one bug that must not exist.
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const TODAY = iso(new Date());
  const daysBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);

  // Captured before anything mutates it: the generated <title> is the fallback
  // for a no-JS view, and the stem every live title is built on.
  const BASE_TITLE = document.title;
  const days = [...document.querySelectorAll(".dl-day")];
  const today = document.querySelector(".dl-day.today");
  const banner = document.getElementById("store-banner");
  const nextEl = document.getElementById("next-up");
  const nextText = nextEl && nextEl.querySelector("p:last-child");
  const entries = [];
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

  // Mirrors _SET in automation/db.py. Keep the two in step.
  const applyLocal = op => {
    const t = state[op.key] || (state[op.key] = { done: false });
    const clearMove = () => { delete t.moved; delete t.reason; delete t.note; delete t.until; };
    if (op.action === "done")          { t.done = true; clearMove(); }
    else if (op.action === "undone")   { t.done = false; }
    else if (op.action === "restored") { clearMove(); }
    else { t.moved = op.action; t.reason = op.reason; t.note = op.note; t.until = op.until; }
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
  const register = (li, dayId, rolled = false) => {
    const box = li.querySelector('input[type="checkbox"]');
    if (!box) return;
    const e = {
      li, box, rolled, dayId,
      id: li.dataset.id,
      key: `${dayId}::${li.dataset.id}`,
      p: Number(li.dataset.p) || 2,
      due: li.dataset.due || dayId,
      needs: (li.dataset.needs || "").split(",").filter(Boolean),
      inToday: !!today && li.closest(".dl-day") === today,
      home: { parent: li.parentNode, next: li.nextSibling },
    };
    entries.push(e);
    box.addEventListener("change", () =>
      act({ key: e.key, action: box.checked ? "done" : "undone" }));
    li.querySelectorAll(".dl-act").forEach(btn =>
      btn.addEventListener("click", ev => {
        ev.preventDefault();
        const action = btn.dataset.act;
        if (action === "restored") act({ key: e.key, action });
        else openDialog(e, action);
      }));
    return e;
  };

  days.forEach(day =>
    day.querySelectorAll(".dl-group:not(.rolled) .dl-list > li")
       .forEach(li => register(li, day.dataset.day)));

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
    });
  }

  // ---- render -------------------------------------------------------------
  const st = key => state[key] || {};
  // A pushed task is only out of the way until its return date arrives.
  const isOut = s => s.moved === "parked" || s.moved === "dropped" ||
                     (s.moved === "pushed" && s.until && s.until > TODAY);

  const dueBadge = e => {
    const s = st(e.key);
    if (s.done || isOut(e)) return null;
    const due = s.moved === "pushed" && s.until ? s.until : e.due;
    if (due < TODAY) {
      const n = daysBetween(due, TODAY);
      return { cls: "red", text: n === 1 ? "1 day overdue" : `${n} days overdue` };
    }
    if (due === TODAY) return { cls: "yellow", text: "due today" };
    return { cls: "fact", text: `due ${due}` };
  };

  function relocate(e) {
    const s = st(e.key);
    let target = e.home.parent;
    if (e.inToday && isOut(s)) {
      const group = document.getElementById(`moved-${s.moved}`);
      if (group) target = group.querySelector(".dl-list");
    }
    if (e.li.parentNode === target) return;
    if (target === e.home.parent) target.insertBefore(e.li, e.home.next);
    else target.appendChild(e.li);
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

  function render() {
    entries.forEach(e => {
      const s = st(e.key);
      const done = s.done === true;
      e.box.checked = done;
      e.li.classList.toggle("done", done);

      const blockers = e.needs.filter(n => st(`${e.dayId}::${n}`).done !== true);
      const waiting = !done && !isOut(s) && blockers.length > 0;
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

    ["parked", "pushed", "dropped"].forEach(kind => {
      const group = document.getElementById(`moved-${kind}`);
      if (!group) return;
      const n = group.querySelectorAll(".dl-list > li").length;
      group.hidden = n === 0;
      group.querySelector(".n").textContent = n;
    });

    days.forEach(day => {
      const count = day.querySelector(".dl-count");
      if (!count) return;
      const mine = entries.filter(e => e.li.closest(".dl-day") === day && !isOut(st(e.key)));
      if (!mine.length) { count.textContent = ""; return; }
      const done = mine.filter(e => st(e.key).done === true).length;
      count.textContent = `${done}/${mine.length} done`;
      count.classList.toggle("all-done", done === mine.length);
    });

    if (!today) return;
    const mine = entries.filter(e => e.inToday && !isOut(st(e.key)));
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
    // Priority decides; an overdue task only breaks a tie within its priority.
    const ready = open
      .filter(e => !e.li.classList.contains("waiting"))
      .sort((a, b) => a.p - b.p || Number(b.rolled) - Number(a.rolled));
    nextEl.hidden = false;
    if (ready.length) {
      const pick = ready[0];
      nextText.innerHTML =
        `<span class="pill ${["", "red", "yellow", "fact"][pick.p]}">P${pick.p}</span> ` +
        pick.li.querySelector(".dl-task").innerHTML +
        (pick.rolled ? ` <span class="dl-from">rolled over from ${pick.dayId}</span>` : "");
    } else if (!open.length) {
      nextText.textContent = mine.length
        ? "Everything on today's list is ticked."
        : "Nothing left on today's list.";
    } else {
      nextText.textContent =
        `Nothing is unblocked — all ${open.length} remaining tasks are waiting on something above.`;
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

  // Rollover: anything from an earlier day that is neither done nor moved out.
  const rolledGroup = document.getElementById("rolled-over");
  if (today && rolledGroup) {
    const list = rolledGroup.querySelector(".dl-list");
    const stale = entries.filter(e =>
      e.dayId !== today.dataset.day && st(e.key).done !== true && !st(e.key).moved);
    stale.forEach(e => {
      const clone = e.li.cloneNode(true);
      const box = clone.querySelector('input[type="checkbox"]');
      const id = `roll-${e.dayId}-${e.id}`;
      box.id = id;
      clone.querySelector("label").setAttribute("for", id);
      const meta = clone.querySelector(".dl-meta");
      if (meta) meta.insertAdjacentHTML("beforeend", `<span class="dl-from">from ${e.dayId}</span>`);
      list.appendChild(clone);
      register(clone, e.dayId, true);
    });
    rolledGroup.hidden = stale.length === 0;
  }

  render();
});
