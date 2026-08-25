// Status tabs + search. Pills carry data-tab; rows carry data-status.
// data-tab="all" shows everything. Counts are filled from the rows.
//
// The rows used to be hand-written markup. They are now rendered from
// /api/jobs by static/apps.js, which calls initTabs() once they are in the DOM
// — so this still self-starts on DOMContentLoaded (a page with static rows
// needs nothing extra) and is safe to call again afterwards.
//
// A row is visible when its TAB matches AND the search box matches. Both live
// in one place on purpose: two scripts each setting `hidden` would fight, and
// whichever ran last would win.
(() => {
  const BASE_TITLE = document.title;
  let current = "all";
  let bound = false;

  const apply = () => {
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
      const slot = p.querySelector(".n");
      if (slot) slot.textContent = n;
      p.setAttribute("aria-current", String(t === current));
    });

    const box = document.getElementById("app-search");
    const q = box ? box.value.trim().toLowerCase() : "";
    rows.forEach(r => {
      const inTab = current === "all" || r.dataset.status === current;
      const hay = r.dataset.search || r.textContent;
      r.hidden = !(inTab && (!q || hay.toLowerCase().includes(q)));
    });

    // With zero rows in the DOM the list has not loaded yet — #app-status is
    // saying so — and "nothing matches" would be a lie. Say it only once there
    // is something to match against.
    const empty = document.getElementById("tab-empty");
    if (empty) empty.hidden = rows.length === 0 || rows.some(r => !r.hidden);
  };

  window.initTabs = () => {
    if (!bound) {
      const pills = document.querySelectorAll("[data-tab]");
      pills.forEach(p => p.addEventListener("click", e => {
        e.preventDefault();
        current = p.dataset.tab;
        apply();
      }));
      const box = document.getElementById("app-search");
      if (box) box.addEventListener("input", apply);
      bound = pills.length > 0;
    }
    apply();
  };

  document.addEventListener("DOMContentLoaded", () => window.initTabs());
})();
