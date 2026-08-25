// Status tabs + search for the launcher, in v1's shape: underlined text tabs
// with a count badge, a right-aligned search box, and rows grouped by intake
// date under a header per group.
//
// THE CONTRACT, unchanged:
//   - tab buttons carry data-tab
//   - rows carry data-status holding the TAB they belong to
//   - every count is derived from the rows in the DOM, never passed in
//   - a group header carries .gcount, which reads the rows visible under it
//
// ⚠ COUNTS ARE A FUNCTION OF THE DOM, NOT OF CALL ORDER. The rows arrive
// asynchronously from /api/jobs, long after DOMContentLoaded. The first version
// of this file counted once on DOMContentLoaded and again only if someone
// remembered to call initTabs() afterwards — so a page whose rows rendered but
// whose initTabs() call did not land showed every tab reading 0 above a full
// list. A MutationObserver on #app-list re-derives the counts whenever its
// contents change, which cannot be got wrong by a caller. initTabs() stays, and
// still works, but nothing depends on it being called.
//
// A row is visible when its TAB matches AND the search box matches. Both live
// in one place on purpose: two scripts each setting `hidden` would fight, and
// whichever ran last would win.
(() => {
  const BASE_TITLE = document.title;
  const DEFAULT_TAB = "ready";
  let current = DEFAULT_TAB;
  let bound = false;
  let watching = false;

  const apply = () => {
    const tabs = [...document.querySelectorAll("[data-tab]")];
    const rows = [...document.querySelectorAll("[data-status]")];
    if (!tabs.length) return;

    // Live tab title: ready-and-unsent is the number that matters here — the
    // backlog gate — so a pinned launcher tab surfaces it without being opened.
    const ready = rows.filter(r => r.dataset.status === "ready").length;
    document.title = ready ? `${ready} ready · unsent · ${BASE_TITLE}` : BASE_TITLE;

    tabs.forEach(t => {
      const name = t.dataset.tab;
      const on = name === current;
      const slot = t.querySelector(".tab-count");
      if (slot) slot.textContent = rows.filter(r => r.dataset.status === name).length;
      t.classList.toggle("active", on);
      t.setAttribute("aria-selected", String(on));
    });

    const box = document.getElementById("app-search");
    const q = box ? box.value.trim().toLowerCase() : "";
    rows.forEach(r => {
      const inTab = r.dataset.status === current;
      const hay = r.dataset.search || r.textContent;
      r.hidden = !(inTab && (!q || hay.toLowerCase().includes(q)));
    });

    // A group whose rows are all filtered out goes away entirely; the ones that
    // remain report how many of their rows this tab is showing, so the header
    // never claims a number the list underneath does not have.
    document.querySelectorAll(".date-group").forEach(g => {
      const shown = [...g.querySelectorAll("[data-status]")].filter(r => !r.hidden).length;
      const slot = g.querySelector(".gcount");
      const next = `${shown} seat${shown === 1 ? "" : "s"}`;
      // ⚠ Only write when it CHANGED. .gcount lives inside #app-list, and
      // assigning textContent replaces child nodes even when the string is
      // identical — which the MutationObserver below would see as a change,
      // calling this again, for ever. The guard is what makes it terminate.
      if (slot && slot.textContent !== next) slot.textContent = next;
      g.hidden = shown === 0;
    });

    // With zero rows in the DOM the list has not loaded yet — #app-status is
    // saying so — and "nothing matches" would be a lie. Say it only once there
    // is something to match against.
    const empty = document.getElementById("tab-empty");
    if (empty) empty.hidden = rows.length === 0 || rows.some(r => !r.hidden);
  };

  // Re-derive whenever the list is rendered, re-rendered or emptied. Only
  // childList is observed: `apply` itself sets `hidden`, an attribute, so it
  // cannot retrigger this.
  const watch = () => {
    const list = document.getElementById("app-list");
    if (watching || !list || typeof MutationObserver === "undefined") return;
    new MutationObserver(apply).observe(list, { childList: true, subtree: true });
    watching = true;
  };

  window.initTabs = () => {
    if (!bound) {
      const tabs = document.querySelectorAll("[data-tab]");
      tabs.forEach(t => t.addEventListener("click", e => {
        e.preventDefault();
        current = t.dataset.tab;
        apply();
      }));
      const box = document.getElementById("app-search");
      if (box) box.addEventListener("input", apply);
      bound = tabs.length > 0;
    }
    watch();
    apply();
  };

  document.addEventListener("DOMContentLoaded", () => window.initTabs());
})();
