// The launcher's Applications list, rendered from PostgreSQL via /api/jobs.
//
// It used to be hand-written markup, which is why the page showed four rows
// while `jobs_tracker` held ninety-two. The database is the search layer;
// directories are storage, not an index.
//
// Served by plain `python -m http.server` there is no API, so the fetch fails.
// That case SAYS SO — an empty list would read as "no applications", which is
// the one wrong answer here.
//
// Rows are built with DOM calls, not innerHTML: every string on them (company,
// role, location) comes out of the database.
(() => {
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  // 88.375 -> "88.4", 83 -> "83". A trailing ".0" reads as false precision.
  const num = v => (Math.round(v * 10) / 10).toString();

  const humanStatus = s => s.replace(/_/g, " ");

  const host = url => {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return null; }
  };

  // Where the card points, and what its path chip should read. A v1 row has no
  // workspace in this repo, so it links out to the posting instead — honest,
  // because there is nothing local to open.
  const target = a => {
    if (a.href) return { href: a.href, chip: a.workspace + "/" };
    if (a.source_url) return { href: a.source_url, chip: (host(a.source_url) || "posting") + " ↗" };
    return { href: null, chip: a.slug + " · no workspace" };
  };

  const card = a => {
    const { href, chip } = target(a);
    const node = el(href ? "a" : "div", "card app");
    if (href) node.href = href;
    node.dataset.status = a.tab;
    // One haystack for the search box, so it matches on company and role even
    // when the visible text has been wrapped or abbreviated.
    node.dataset.search = [a.company, a.role, a.slug, a.location].filter(Boolean).join(" ");

    node.append(el("strong", null, `${a.company} — ${a.role}`));

    const meta = el("span", "app-meta");
    // Technical is the score that matters; non-technical is informational and
    // never a gate. The styling says so — accent versus plain.
    meta.append(el("span", "app-score tech",
      a.technical == null ? "technical —" : `technical ${num(a.technical)}`));
    meta.append(el("span", "app-score func",
      a.non_technical == null ? "non-technical —" : `non-technical ${num(a.non_technical)}`));
    meta.append(el("span", "app-stat", humanStatus(a.status)));
    if (a.location) meta.append(el("span", "app-loc", a.location));
    node.append(meta);

    node.append(el("span", "path", chip));
    return node;
  };

  const say = (msg, bad) => {
    const s = document.getElementById("app-status");
    if (!s) return;
    s.textContent = msg;
    s.className = bad ? "app-status bad" : "app-status";
    s.hidden = !msg;
  };

  document.addEventListener("DOMContentLoaded", async () => {
    const list = document.getElementById("app-list");
    if (!list) return;
    let data;
    try {
      const r = await fetch("/api/jobs");
      if (!r.ok) throw new Error(`the server answered ${r.status}`);
      data = await r.json();
    } catch (err) {
      say(`Applications are unavailable — ${err.message}. This list comes from the `
        + `jobs_tracker database, which needs automation/serve.py rather than `
        + `python -m http.server. Nothing has been lost; the page just cannot read it.`, true);
      return;
    }
    list.replaceChildren(...data.applications.map(card));
    say("");
    window.initTabs();
  });
})();
