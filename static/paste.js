// Paste-sheet progress. Ticking a section survives reloads, because building a
// Hiration card is a long sitting and losing your place means re-reading ten
// blocks to work out which ones already went in.
//
// localStorage, not the daily-log database: this is per-card scratch state, not
// a task, and it must keep working when serve.py is not the thing on 8006.
document.addEventListener("DOMContentLoaded", () => {
  const KEY = "v2-paste-" + (document.body.dataset.sheet || "master");
  let done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { done = {} }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(done)); } catch {} };

  const boxes = [...document.querySelectorAll(".ps-done")];
  const counter = document.getElementById("ps-count");
  const BASE = document.title;

  const tally = () => {
    const n = boxes.filter(b => b.checked).length;
    if (counter) counter.textContent = `${n}/${boxes.length} pasted`;
    document.title = n ? `${n}/${boxes.length} · ${BASE}` : BASE;
  };

  boxes.forEach(b => {
    b.checked = done[b.dataset.sec] === true;
    b.closest("section").classList.toggle("pasted", b.checked);
    b.addEventListener("change", () => {
      done[b.dataset.sec] = b.checked;
      b.closest("section").classList.toggle("pasted", b.checked);
      save(); tally();
    });
  });
  tally();

  const reset = document.getElementById("ps-reset");
  if (reset) reset.addEventListener("click", () => {
    done = {}; save();
    boxes.forEach(b => { b.checked = false; b.closest("section").classList.remove("pasted"); });
    tally();
  });
});
