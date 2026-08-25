// Daily log: checkbox state, priority-aware "do next", dependency gating and
// rollover. State is one localStorage object keyed "<day>::<task id>".
//
// A task can be rendered twice — once on its own day, and again in today's
// rolled-over list — and both renderings share a single state key, so ticking
// either one ticks both. days.json never duplicates a task; the rolled-over
// list is built here at load time, because Python cannot see localStorage.
document.addEventListener("DOMContentLoaded", () => {
  const KEY = "v2-daily-todo";
  let state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { state = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {} };
  const isDone = k => state[k] === true;

  const days = [...document.querySelectorAll(".dl-day")];
  const today = document.querySelector(".dl-day.today");
  const entries = [];

  const register = (li, dayId, rolled = false) => {
    const box = li.querySelector('input[type="checkbox"]');
    if (!box) return;
    const entry = {
      li, box, rolled, dayId,
      id: li.dataset.id,
      key: `${dayId}::${li.dataset.id}`,
      p: Number(li.dataset.p) || 2,
      needs: (li.dataset.needs || "").split(",").filter(Boolean),
    };
    entries.push(entry);
    box.addEventListener("change", () => {
      state[entry.key] = box.checked;
      save();
      render();
    });
  };

  days.forEach(day => {
    day.querySelectorAll(".dl-group:not(.rolled) .dl-list > li")
       .forEach(li => register(li, day.dataset.day));
  });

  // ---- rollover -----------------------------------------------------------
  const rolledGroup = document.getElementById("rolled-over");
  if (today && rolledGroup) {
    const list = rolledGroup.querySelector(".dl-list");
    const stale = entries.filter(e => e.dayId !== today.dataset.day && !isDone(e.key));
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

  // ---- render -------------------------------------------------------------
  const nextEl = document.getElementById("next-up");
  const nextText = nextEl && nextEl.querySelector("p:last-child");

  const render = () => {
    entries.forEach(e => {
      const done = isDone(e.key);
      e.box.checked = done;
      e.li.classList.toggle("done", done);
      // A prerequisite is only ever satisfied on its OWN day.
      const blockers = e.needs.filter(n => !isDone(`${e.dayId}::${n}`));
      const waiting = !done && blockers.length > 0;
      e.li.classList.toggle("waiting", waiting);
      const meta = e.li.querySelector(".dl-meta");
      let hint = e.li.querySelector(".dl-waiting");
      if (waiting && meta) {
        if (!hint) {
          hint = document.createElement("span");
          hint.className = "dl-waiting";
          meta.appendChild(hint);
        }
        hint.textContent = blockers.length === 1
          ? "waiting on 1 task"
          : `waiting on ${blockers.length} tasks`;
      } else if (hint) {
        hint.remove();
      }
    });

    days.forEach(day => {
      const count = day.querySelector(".dl-count");
      if (!count) return;
      const mine = entries.filter(e => e.li.closest(".dl-day") === day);
      if (!mine.length) { count.textContent = ""; return; }
      const done = mine.filter(e => isDone(e.key)).length;
      count.textContent = `${done}/${mine.length} done`;
      count.classList.toggle("all-done", done === mine.length);
    });

    if (!nextText || !today) return;
    const mine = entries.filter(e => e.li.closest(".dl-day") === today);
    const open = mine.filter(e => !isDone(e.key));
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
      nextText.textContent = "Everything on today's list is ticked.";
    } else {
      nextText.textContent =
        `Nothing is unblocked — all ${open.length} remaining tasks are waiting on something above.`;
    }
  };

  render();
});
