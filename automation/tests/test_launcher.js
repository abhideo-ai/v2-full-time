// The launcher's Applications list, end to end: index.html + static/tabs.js +
// static/apps.js against a real serve.py and a real jobs_tracker.
//
//   argv[2]  API   — serve.py, database reachable
//   argv[3]  PLAIN — plain http.server, so /api/jobs 404s
//   argv[4]  DOWN  — serve.py pointed at a database that does not exist (503)
//
// The two failure modes matter as much as the happy path: the page must SAY the
// list is unavailable, never render an empty grid that reads as "no applications".
//
// ⚠ Section 3 is a REGRESSION TEST for a real defect: every tab count read 0
// while rows were plainly rendered underneath. Counts must be a function of the
// DOM, not of whether someone remembered to call initTabs() after the fetch.
const fs = require("fs"), { JSDOM } = require("jsdom");
const REPO = require("path").resolve(__dirname, "../..");
const [API, PLAIN, DOWN] = process.argv.slice(2);
let P = 0, F = 0;
const ok = (c, l) => { c ? P++ : F++; console.log(`  ${c ? "PASS" : "FAIL"}  ${l}`); };
const settle = (ms = 120) => new Promise(r => setTimeout(r, ms));

async function boot(base) {
  const html = fs.readFileSync(REPO + "/index.html", "utf8");
  const dom = new JSDOM(html, { url: base + "/", runScripts: "outside-only" });
  const w = dom.window;
  w.fetch = (u, o) => fetch(u.startsWith("http") ? u : base + u, o);
  for (const f of ["/static/tabs.js", "/static/apps.js"]) w.eval(fs.readFileSync(REPO + f, "utf8"));
  await new Promise(res => {
    if (w.document.readyState !== "loading") return res();
    w.document.addEventListener("DOMContentLoaded", res, { once: true });
    setTimeout(res, 2000);
  });
  await settle(350);
  return w;
}
const rows    = d => [...d.querySelectorAll("#app-list [data-status]")];
const visible = d => rows(d).filter(r => !r.hidden);
const tab     = (d, t) => d.querySelector(`[data-tab="${t}"]`);
const countOf = (d, t) => Number(tab(d, t).querySelector(".tab-count").textContent);
const click   = async (w, t) => {
  tab(w.document, t).dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
};
const type    = async (w, q) => {
  const box = w.document.getElementById("app-search");
  box.value = q;
  box.dispatchEvent(new w.Event("input"));
  await settle(30);
};

(async () => {
  const api = JSON.parse(await (await fetch(API + "/api/jobs")).text());
  const total = api.applications.length;
  const TABS = ["ready", "applied", "closed", "heard-back", "not-selected", "other"];

  console.log("\n1. Rendered from the database, as rows and not cards");
  let w = await boot(API), d = w.document;
  ok(rows(d).length === total, `every row reached the page — ${rows(d).length} of ${total}`);
  ok(total > 4, `and it is the whole database, not the four directories — ${total} rows`);
  ok(d.getElementById("app-status").hidden, "the loading message goes away");
  ok(d.getElementById("tab-empty").hidden, "and it does not claim nothing matches");
  ok(d.querySelectorAll("#app-list .card").length === 0, "nothing renders as a card any more");
  ok(rows(d).every(r => r.tagName === "LI" && r.querySelector(".jrow")),
     "every seat is an <li> with a .jrow of columns");
  ok(d.querySelectorAll("#app-list .date-group").length === api.groups.length,
     `one group per intake date — ${api.groups.length}`);
  ok([...d.querySelectorAll(".date-group")].every(g => g.querySelector(".jhead")),
     "each group carries its own COMPANY · TITLE · TECH · NON-TECH header strip");

  console.log("\n2. Counts, and the tab contract");
  let sum = 0;
  for (const t of TABS) {
    ok(countOf(d, t) === api.counts[t], `${t} tab says ${countOf(d, t)}, the API says ${api.counts[t]}`);
    sum += countOf(d, t);
  }
  ok(sum === total, `the tabs account for every row — ${sum} of ${total}`);
  ok(!d.querySelector('[data-tab="all"]'), "there is no `all` tab to sweep archived rows back in");
  const readyN = api.counts.ready;
  ok(readyN ? d.title.startsWith(`${readyN} ready · unsent ·`) : true,
     `the title leads with ready-and-unsent — got "${d.title}"`);
  ok(tab(d, "ready").classList.contains("active"), "`ready to apply` is the tab that opens");

  console.log("\n3. REGRESSION — a count never reads 0 while rows are on the page");
  const present = t => rows(d).filter(r => r.dataset.status === t).length;
  for (const t of TABS) {
    ok(!(countOf(d, t) === 0 && present(t) > 0),
       `${t}: ${present(t)} row(s) in the DOM, tab reads ${countOf(d, t)}`);
  }
  ok(TABS.some(t => countOf(d, t) > 0), "at least one tab is non-zero — the counts really ran");
  // The structural guarantee: re-render the list WITHOUT calling initTabs and
  // the counts must follow anyway. This is the defect, reproduced.
  const list = d.getElementById("app-list");
  const kept = [...list.children];
  list.replaceChildren();
  await settle(60);
  ok(TABS.every(t => countOf(d, t) === 0), "an emptied list drops every count to 0");
  list.append(...kept);                       // note: initTabs() is NOT called
  await settle(60);
  ok(TABS.every(t => countOf(d, t) === api.counts[t]),
     "and re-rendered rows restore every count with no initTabs() call at all");
  ok(rows(d).length === total, "with every row back on the page");

  console.log("\n4. Archived rows never reach the page at all");
  for (const t of TABS) {
    await click(w, t);
    ok(visible(d).every(r => r.dataset.status === t), `the ${t} tab shows only ${t} rows`);
  }
  ok(!d.querySelector('[data-tab="archived"]'), "there is no archived tab to click");
  ok(rows(d).every(r => r.dataset.status !== "archived"),
     "and no archived row is in the DOM, hidden or otherwise");
  ok(api.counts.archived > 0,
     `the API still reports ${api.counts.archived} archived — they are filtered at render, not deleted`);
  await click(w, "ready");
  ok(visible(d).length === api.counts.ready, `ready shows ${visible(d).length} of ${api.counts.ready}`);
  ok(tab(d, "ready").getAttribute("aria-selected") === "true", "the tab marks itself selected");

  console.log("\n5. Group headers say what is derivable and nothing else");
  const groupsShown = [...d.querySelectorAll(".date-group")].filter(g => !g.hidden);
  ok(groupsShown.length > 0, `${groupsShown.length} group(s) visible on the ready tab`);
  ok(groupsShown.every(g => {
    const shown = [...g.querySelectorAll("[data-status]")].filter(r => !r.hidden).length;
    return g.querySelector(".gcount").textContent === `${shown} seat${shown === 1 ? "" : "s"}`;
  }), "each header counts the rows it is actually showing");
  ok([...d.querySelectorAll(".date-group")].every(g => g.hidden ||
       [...g.querySelectorAll("[data-status]")].some(r => !r.hidden)),
     "a group with nothing visible under it is hidden entirely");
  ok(groupsShown.every(g => /^\d{4}-\d{2}-\d{2}$/.test(g.querySelector("h2").firstChild.textContent.trim())),
     "every header opens with an ISO intake date");
  const authored = api.groups.filter(g => g.note).length;
  ok(groupsShown.every(g => /^—\s*\d+ seats?$/.test(g.querySelector(".descriptor").textContent.trim()))
       || authored > 0,
     `no header invents a narrative — ${authored} hand-authored note(s) on file`);

  console.log("\n6. Search filters on company and role, and composes with the tab");
  await click(w, "archived");
  const probe = api.applications.find(a => a.status === "archived").company.split(" ")[0].toLowerCase();
  await type(w, probe);
  const hits = visible(d);
  ok(hits.length > 0 && hits.length < total, `"${probe}" narrows the list to ${hits.length}`);
  ok(hits.every(r => r.dataset.search.toLowerCase().includes(probe)), "every hit really matches");
  ok(hits.every(r => r.dataset.status === "archived"), "a filtered tab stays filtered while searching");
  await type(w, "zzzznotacompany");
  ok(visible(d).length === 0, "a miss shows nothing");
  ok(!d.getElementById("tab-empty").hidden, "and says so");
  await type(w, "");
  ok(visible(d).length === api.counts.archived, "clearing the box restores the tab");

  console.log("\n7. Both scores are columns, and nothing incomparable is shown as a number");
  const cell = (r, cls) => r.querySelector(cls).textContent.trim();
  const find = slug => [...rows(d)].find(r => r.dataset.search.includes(slug));
  const v1 = api.applications.find(a => a.rubric === "v1-five-axis");
  if (v1) {
    const r = find(v1.slug);
    ok(cell(r, ".jc-tech") === "v1" && cell(r, ".jc-nt") === "v1",
       "a v1-rubric row names its rubric instead of a number that would invite a ranking");
    ok(r.querySelector(".jc-tech").title.includes("not comparable"), "and says why on hover");
    ok(r.querySelector(".jrow-detail").textContent.includes("v1 five-axis triage"),
       "the rescaled figures are still there, in the expanded row, labelled");
  } else ok(true, "no v1-rubric row to check");
  await click(w, "ready");
  const v2 = api.applications.find(a => a.rubric === "v2-weighted");
  if (v2) {
    const r = find(v2.slug);
    ok(/^\d+(\.\d)?$/.test(cell(r, ".jc-tech")), `a v2 seat shows its number — ${cell(r, ".jc-tech")}`);
  } else ok(true, "no v2-scored seat to check");
  const un = api.applications.find(a => a.technical == null && a.rubric == null);
  if (un) ok(cell(find(un.slug), ".jc-tech") === "—", "an unscored seat reads as a dash, never a number");
  else ok(true, "no unscored seat to check");
  ok(rows(d).every(r => r.querySelector(".jc-tech") && r.querySelector(".jc-nt")),
     "every row carries both score columns");

  console.log("\n8. The caret expands to something real");
  const first = visible(d)[0];
  const det = first.querySelector(".jrow-detail");
  ok(det && det.hidden, "the detail starts closed");
  first.querySelector(".jtog").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
  ok(!det.hidden && first.classList.contains("open"), "the caret opens it");
  ok(det.textContent.includes("status:") && det.textContent.includes("slug:"),
     "and it reveals real facts, not an empty box");
  first.querySelector(".jtog").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
  ok(det.hidden, "and closes it again");

  console.log("\n9. Compensation never reaches the page");
  ok(!/salary|₹|lacs|lpa/i.test(d.getElementById("app-list").textContent),
     "no compensation on any row — it is deferred");

  console.log("\n10. Plain http.server — says so, does not render an empty list");
  w = await boot(PLAIN); d = w.document;
  const s = d.getElementById("app-status");
  ok(!s.hidden && s.className.includes("bad"), "the page reports the failure");
  ok(s.textContent.includes("serve.py"), "and says how to fix it");
  ok(rows(d).length === 0, "no rows rendered");
  ok(d.getElementById("tab-empty").hidden,
     "and it does NOT say \"no applications match\" — that would be a lie");

  console.log("\n11. Database unreachable — 503, and the page still renders");
  const r503 = await fetch(DOWN + "/api/jobs");
  ok(r503.status === 503, `/api/jobs answers 503 — got ${r503.status}`);
  ok((await r503.json()).error.includes("database unreachable"), "and says why");
  ok((await fetch(DOWN + "/index.html")).status === 200, "index.html still answers 200");
  w = await boot(DOWN); d = w.document;
  ok(!d.getElementById("app-status").hidden, "the page reports it");
  ok(d.getElementById("app-status").textContent.includes("503"), "naming the status it got");
  ok(d.querySelector("h1").textContent.includes("Full-time JD workspace"),
     "and the rest of the launcher renders regardless");

  console.log(`\n${P} passed, ${F} failed`);
  process.exit(F ? 1 : 0);
})();
