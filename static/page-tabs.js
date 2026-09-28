// Section tabs for a workspace page (templates/workspace/index.html). static/workspace.js
// builds the tab bar and the panels from workspace.json, loads every tab's file, and
// then calls PageTabs.init().
//
// THE CONTRACT:
//   - tab buttons are .status-tab[data-panel] inside [data-page-tabs]
//   - each panel is a section[data-panel] with the same name, and id = that name
//   - one panel shows at a time, via the `hidden` attribute
//   - the URL hash picks the tab (index.html#questions). A hash naming something INSIDE
//     a panel (index.html#flags) opens that panel and every fold around it, then scrolls
//     to it; an unknown hash shows the first panel
//   - print shows every panel (style.css)
//
// The launcher's static/tabs.js is a different thing (rows, counts, search); this
// file only switches sections.
window.PageTabs = {
  init() {
    const tabs = [...document.querySelectorAll("[data-page-tabs] .status-tab[data-panel]")];
    const panels = [...document.querySelectorAll("section[data-panel]")];
    if (!tabs.length || !panels.length) return;
    const names = tabs.map((t) => t.dataset.panel);

    function show(name, focus) {
      if (!names.includes(name)) name = names[0];
      for (const t of tabs) {
        const on = t.dataset.panel === name;
        t.classList.toggle("active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        if (on && focus) t.focus();
      }
      for (const p of panels) p.hidden = p.dataset.panel !== name;
    }

    function go(name, focus) {
      history.replaceState(null, "", "#" + name);
      show(name, focus);
    }

    tabs.forEach((t, i) => {
      t.addEventListener("click", () => go(t.dataset.panel));
      t.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        const step = e.key === "ArrowRight" ? 1 : tabs.length - 1;
        go(tabs[(i + step) % tabs.length].dataset.panel, true);
      });
    });
    // A hash can name a panel (#research) or an element inside one (#flags): either
    // way the panel holding it opens. An inner target also has its folds opened (the
    // target itself, when it is a fold) and is scrolled into view — the browser's own
    // jump happened while that panel was still hidden.
    function follow(hash) {
      if (!hash || names.includes(hash)) return show(hash);
      const el = document.getElementById(hash);
      const panel = el && el.closest("section[data-panel]");
      show(panel ? panel.dataset.panel : "");
      if (!panel) return;
      for (let d = el.closest("details"); d; d = d.parentElement.closest("details")) d.open = true;
      el.scrollIntoView();
    }

    window.addEventListener("hashchange", () => follow(decodeURIComponent(location.hash.slice(1))));
    follow(decodeURIComponent(location.hash.slice(1)));
  },
};
