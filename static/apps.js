// The launcher's Applications list, rendered from PostgreSQL via /api/jobs, in
// v1's shape: one ROW per slug, grouped by the date the seat came in, with a
// column header strip per group and an expandable detail row.
//
// It used to be hand-written markup, which is why the page once showed four rows
// while the database held ninety-two. The database is the search layer;
// directories are storage, not an index.
//
// The database behind /api/jobs is `jobs_tracker_v2`. v1's ninety-two rows are
// in `jobs_tracker` and are not served here at all — see automation/jobs_db.py.
//
// Served by plain `python -m http.server` there is no API, so the fetch fails.
// That case SAYS SO — an empty list would read as "no applications", which is
// the one wrong answer here.
//
// Rows are built with DOM calls, not innerHTML: every string on them (company,
// role, location) comes out of the database.
//
// Filtering, counting and group visibility belong to static/tabs.js, which
// watches this list and re-derives them whenever it changes.
(() => {
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  const li = (...kids) => { const n = el("li"); n.append(...kids); return n; };

  const link = (href, text, external) => {
    const a = el("a", null, text);
    a.href = href;
    if (external) { a.target = "_blank"; a.rel = "noopener"; }
    return a;
  };

  // 88.375 -> "88.4", 83 -> "83". A trailing ".0" reads as false precision.
  const num = v => (Math.round(v * 10) / 10).toString();

  const human = s => (s || "").replace(/_/g, " ");

  const host = url => {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return null; }
  };

  // "o9 Solutions (via Recruit Right)" -> ["o9 Solutions", "(via Recruit Right)"]
  // The source is already written into the company field on the rows that have
  // one, so this splits what is there rather than inventing an attribution.
  const splitCompany = name => {
    const m = /^(.*\S)\s*(\([^()]*\))\s*$/.exec(name || "");
    return m ? [m[1], m[2]] : [name || "", null];
  };

  // Where the row points, and what its detail should call that. A v1 row has no
  // workspace in this repo, so it links out to the posting instead — honest,
  // because there is nothing local to open.
  const target = a => {
    if (a.href) return { href: a.href, label: a.workspace + "/ →", external: false };
    if (a.source_url) return { href: a.source_url, label: (host(a.source_url) || "posting") + " ↗", external: true };
    return { href: null, label: null };
  };

  // ⚠ A v1 row's scores come off v1's five-axis TRIAGE rubric, rescaled. They
  // are not a v2 technical match and reading "20" beside "88.4" invites a
  // ranking that does not exist. So the columns say which rubric produced the
  // row and the numbers themselves move into the detail, where they can be
  // labelled. Nothing is discarded — `fit_breakdown` still holds them.
  const V1 = "v1-five-axis";
  const scoreCell = (a, value, cls) => {
    if (a.rubric === V1) {
      const n = el("span", cls + " jc-v1", "v1");
      n.title = "scored on v1's five-axis triage rubric — not comparable to a v2 technical score";
      return n;
    }
    return el("span", cls, value == null ? "—" : num(value));
  };

  const detail = a => {
    const box = el("div", "jrow-detail");
    box.hidden = true;
    const two = el("div", "jd-two");

    const links = el("ul", "jbul");
    const t = target(a);
    if (t.href) links.append(li(link(t.href, t.label, t.external)));
    if (a.href && a.source_url) {
      links.append(li(link(a.source_url, (host(a.source_url) || "posting") + " ↗", true)));
    }
    if (a.source_note) links.append(li(el("span", "muted", a.source_note)));
    if (!links.childElementCount) links.append(li(el("span", "muted", "no workspace, no posting URL")));

    const facts = el("ul", "jbul");
    facts.append(li(el("span", null, `status: ${human(a.status)}`)));
    if (a.location) facts.append(li(el("span", null, `location: ${a.location}`)));
    if (a.at) facts.append(li(el("span", null, `${a.at_kind} ${a.at.slice(0, 10)}`)));
    facts.append(li(el("span", null, `slug: ${a.slug}`)));
    if (a.rubric === V1) {
      facts.append(li(el("span", null,
        `v1 five-axis triage — technical ${a.technical == null ? "—" : num(a.technical)}`
        + ` · non-technical ${a.non_technical == null ? "—" : num(a.non_technical)}`
        + " (not comparable to a v2 weighted total)")));
    } else if (a.rubric) {
      facts.append(li(el("span", null, `rubric: ${a.rubric}`)));
    }

    two.append(links, facts);
    box.append(two);
    return box;
  };

  const row = a => {
    const node = el("li");
    node.dataset.status = a.tab;
    // One haystack for the search box, so it matches on company and role even
    // when the visible text has been wrapped or abbreviated.
    node.dataset.search = [a.company, a.role, a.slug, a.location].filter(Boolean).join(" ");

    const jrow = el("div", "jrow");
    const tog = el("button", "jtog", "▸");
    tog.type = "button";
    tog.setAttribute("aria-expanded", "false");
    tog.setAttribute("aria-label", "Expand row");
    jrow.append(tog);

    const [name, src] = splitCompany(a.company);
    const co = el("span", "jc jc-co");
    const t = target(a);
    co.append(t.href ? link(t.href, name, t.external) : el("span", null, name));
    if (src) co.append(el("span", "jc-src", src));
    jrow.append(co);

    jrow.append(el("span", "jc jc-title", a.role));
    jrow.append(scoreCell(a, a.technical, "jc jc-tech"));
    jrow.append(scoreCell(a, a.non_technical, "jc jc-nt"));

    const box = detail(a);
    node.append(jrow, box);

    const toggle = () => {
      const open = node.classList.toggle("open");
      box.hidden = !open;
      tog.setAttribute("aria-expanded", String(open));
    };
    tog.addEventListener("click", e => { e.stopPropagation(); e.preventDefault(); toggle(); });
    jrow.addEventListener("click", e => { if (!e.target.closest("a, button")) toggle(); });
    return node;
  };

  const HEADS = ["", "Company", "Title", "Tech", "Non-tech"];

  const group = (g, rows) => {
    const box = el("div", "date-group");

    const h = el("h2", null, g.date || "undated");
    const d = el("span", "descriptor", "— ");
    // The count is filled by tabs.js from the rows this tab actually shows, so
    // the header can never claim more than the list beneath it.
    d.append(el("span", "gcount", ""));
    // ⚠ Anything after the count is HAND-AUTHORED in automation/intake_notes.json
    // and absent until he writes it. Never composed here from a row count.
    if (g.note) d.append(el("span", null, " · " + g.note));
    h.append(d);
    box.append(h);

    const head = el("div", "jhead");
    head.setAttribute("aria-hidden", "true");
    HEADS.forEach(t => head.append(el("span", null, t)));
    box.append(head);

    const list = el("ul", "app-list");
    list.append(...rows.map(row));
    box.append(list);
    return box;
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
    const by = new Map();
    // Every row is rendered. There is nothing to filter out: `jobs_tracker_v2`
    // holds v2's seats and only v2's seats, and v1's ninety-two live in a
    // database this page never opens. The archived tab and the filter that once
    // stood here both came out on 2026-08-26 with db/migrations/006.
    data.applications.forEach(a => {
      const k = a.intake || "";
      if (!by.has(k)) by.set(k, []);
      by.get(k).push(a);
    });
    list.replaceChildren(...data.groups.map(g => group(g, by.get(g.date || "") || [])));
    say("");
    window.initTabs();
  });
})();
