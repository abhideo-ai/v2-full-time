// Status tabs. Pills carry data-tab; rows carry data-status.
// data-tab="all" shows everything. Counts are filled from the rows.
document.addEventListener("DOMContentLoaded", () => {
  const BASE_TITLE = document.title;
  const pills = [...document.querySelectorAll("[data-tab]")];
  const rows  = [...document.querySelectorAll("[data-status]")];
  if (!pills.length) return;

  // Live tab title: ready-and-unsent is the number that matters here — the
  // backlog gate — so a pinned launcher tab surfaces it without being opened.
  const ready = rows.filter(r => r.dataset.status === "ready").length;
  document.title = ready ? `${ready} ready · unsent · ${BASE_TITLE}` : BASE_TITLE;

  pills.forEach(p => {
    const t = p.dataset.tab;
    const n = t === "all" ? rows.length : rows.filter(r => r.dataset.status === t).length;
    p.querySelector(".n").textContent = n;
  });

  const show = t => {
    pills.forEach(p => p.setAttribute("aria-current", String(p.dataset.tab === t)));
    rows.forEach(r => { r.hidden = t !== "all" && r.dataset.status !== t; });
    const empty = document.getElementById("tab-empty");
    if (empty) empty.hidden = rows.some(r => !r.hidden);
  };

  pills.forEach(p => p.addEventListener("click", e => { e.preventDefault(); show(p.dataset.tab); }));
  show("all");
});
