// The workspace page. Every workspace's index.html is the same thin shell, copied from
// templates/workspace/index.html; this file fills it in from three sources:
//
//   workspace.json    the manifest: slug, company, role, route, received date, the
//                     résumé-changes file, and the tabs specific to this job
//   one file per tab  a standalone page; what its <main> holds is shown in the tab
//   /api/jobs?slug=   tracker status and technical score from jobs_tracker_v2, so the
//                     header cannot go stale
//
// and then hands switching to static/page-tabs.js.
//
// THE TAB-FILE CONTRACT (templates/workspace/ has an example of each static tab):
//   - a plain page that opens on its own; the tab shows what its <main> holds
//   - elements marked data-standalone (breadcrumb, page title) show only on their own
//   - no <style>; no <script> except the shared static/copy.js after </main>, which
//     keeps a page's copy buttons working when it is opened on its own
//   - ids unique across every file in the workspace
//   - folds are <details><summary>…</summary><div>…</div></details>; the first is open
//   - a link to another tab's file (kim.html#posts) is kept inside index.html (#posts)
//
// Every tab loads at once, so links between tabs can land. A tab whose file is missing
// says so; it is never dropped, so every workspace shows the same six static tabs in
// the same order.
(() => {
  // Tabs named in workspace.json's "tabs" go right after Research.
  const STATIC = [
    { id: "overview", label: "Overview", src: "overview.html" },
    { id: "jd", label: "Job description", src: "jd.html" },
    { id: "score", label: "Tech score gaps", src: "score.html" },
    { id: "resume", label: "Résumé changes", src: null }, // workspace.json's "resume_changes"
    { id: "research", label: "Research", src: "research.html" },
    { id: "questions", label: "Open questions", src: "questions.html" },
  ];
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"];
  const byId = (id) => document.getElementById(id);

  function el(tag, attrs, text) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text != null) n.textContent = text;
    return n;
  }

  async function get(src) {
    const r = await fetch(src);
    if (r.status === 404) throw new Error(`${src} has not been written`);
    if (!r.ok) throw new Error(`${src} could not be loaded (HTTP ${r.status})`);
    return r;
  }

  function tabsOf(m) {
    const tabs = STATIC.map((t) => (t.id === "resume" ? { ...t, src: m.resume_changes || null } : t));
    tabs.splice(tabs.findIndex((t) => t.id === "research") + 1, 0, ...(m.tabs || []));
    const ids = tabs.map((t) => t.id);
    const twice = ids.find((id, i) => ids.indexOf(id) !== i);
    if (twice) throw new Error(`workspace.json uses the tab id "${twice}" twice`);
    return tabs;
  }

  function header(m) {
    const [y, mo, d] = m.received.split("-");
    const up = "../../../index.html";
    const crumbs = byId("ws-crumbs");
    [[up, "Full-time JD (job description) workspace"],
     [`${up}?month=${y}-${mo}`, `${MONTHS[mo - 1]}-${y}`],
     [`${up}?date=${m.received}`, d],
     [`${up}?q=${encodeURIComponent(m.slug)}`, m.slug],
    ].forEach(([href, text], i) => {
      if (i) crumbs.append(" › ");
      crumbs.append(el("a", { href }, text));
    });
    byId("ws-company").textContent = m.company;
    byId("ws-role").textContent = [m.role, m.route].filter(Boolean).join(" · ");
    document.title = `${m.company} · ${m.role}`;
  }

  function frame(tabs) {
    const bar = document.querySelector("[data-page-tabs] .status-tabs");
    for (const t of tabs) {
      bar.append(el("button", { class: "status-tab", type: "button", "data-panel": t.id,
        role: "tab", "aria-selected": "false" }, t.label));
      byId("ws-panels").append(el("section", { class: "wl-job", id: t.id, "data-panel": t.id,
        role: "tabpanel", "aria-label": t.label }));
    }
  }

  async function fill(t) {
    const panel = byId(t.id);
    try {
      if (!t.src) throw new Error("workspace.json names no file for this tab");
      const doc = new DOMParser().parseFromString(await (await get(t.src)).text(), "text/html");
      const main = doc.querySelector("main");
      if (!main) throw new Error(`${t.src} has no <main>`);
      main.querySelectorAll("[data-standalone]").forEach((n) => n.remove());
      panel.innerHTML = main.innerHTML;
    } catch (e) {
      panel.append(el("p", { class: "dim" }, `Nothing here yet: ${e.message}.`));
    }
  }

  // kim.html#posts -> #posts, research.html -> #research: a link between tabs stays here.
  function localise(tabs) {
    const tabFor = new Map(tabs.filter((t) => t.src)
      .map((t) => [new URL(t.src, location.href).pathname, t.id]));
    for (const a of document.querySelectorAll("#ws-panels a[href]")) {
      const u = new URL(a.getAttribute("href"), location.href);
      const id = u.origin === location.origin && tabFor.get(u.pathname);
      if (id) a.setAttribute("href", u.hash || "#" + id);
    }
  }

  async function status(slug) {
    const box = byId("ws-status");
    const pill = (kind, text) => box.append(el("span", { class: `pill ${kind}`.trim() }, text));
    try {
      const r = await fetch("/api/jobs?slug=" + encodeURIComponent(slug));
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const row = (await r.json()).applications[0];
      if (!row) return pill("warn", "not in the tracker");
      pill("fact", `tracker: ${row.status.replace(/_/g, " ")}`);
      pill("", row.technical == null ? "not scored" : `technical ${row.technical}`);
    } catch (e) {
      pill("warn", `tracker unavailable (${e.message})`);
    }
  }

  // style.css prints every tab; this prints every fold too, then puts them back.
  addEventListener("beforeprint", () => document.querySelectorAll("details:not([open])")
    .forEach((d) => { d.open = true; d.dataset.printOpened = ""; }));
  addEventListener("afterprint", () => document.querySelectorAll("details[data-print-opened]")
    .forEach((d) => { d.open = false; delete d.dataset.printOpened; }));

  (async () => {
    try {
      const m = await (await get("workspace.json")).json();
      const tabs = tabsOf(m);
      header(m);
      frame(tabs);
      status(m.slug); // not awaited: the tabs never wait on the database
      await Promise.all(tabs.map(fill));
      localise(tabs);
      PageTabs.init();
    } catch (e) {
      const p = byId("ws-error");
      p.textContent = `This page could not be built: ${e.message}. It needs automation/serve.py ` +
        "(http://localhost:8006); a file opened straight from disk cannot load its tabs.";
      p.hidden = false;
    }
  })();
})();
