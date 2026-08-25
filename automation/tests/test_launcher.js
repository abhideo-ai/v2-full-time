// The launcher's Applications list, end to end: index.html + static/tabs.js +
// static/apps.js against a real serve.py and a real jobs_tracker.
//
//   argv[2]  API   — serve.py, database reachable
//   argv[3]  PLAIN — plain http.server, so /api/jobs 404s
//   argv[4]  DOWN  — serve.py pointed at a database that does not exist (503)
//
// The two failure modes matter as much as the happy path: the page must SAY the
// list is unavailable, never render an empty grid that reads as "no applications".
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
const pill    = (d, t) => d.querySelector(`[data-tab="${t}"]`);
const type    = async (w, q) => {
  const box = w.document.getElementById("app-search");
  box.value = q;
  box.dispatchEvent(new w.Event("input"));
  await settle(30);
};

(async () => {
  const api = JSON.parse(await (await fetch(API + "/api/jobs")).text());
  const total = api.applications.length;

  console.log("\n1. Rendered from the database");
  let w = await boot(API), d = w.document;
  ok(rows(d).length === total, `every row reached the page — ${rows(d).length} of ${total}`);
  ok(total > 4, `and it is the whole database, not the four directories — ${total} rows`);
  ok(d.getElementById("app-status").hidden, "the loading message goes away");
  ok(d.getElementById("tab-empty").hidden, "and it does not claim nothing matches");
  ok(!d.documentElement.outerHTML.includes("<!-- <a class=\"card\" data-status=\"ready\""),
     "the hand-written card template is gone from the markup");

  console.log("\n2. The tab contract still holds");
  ok(Number(pill(d, "all").querySelector(".n").textContent) === total, "the `all` pill counts them");
  let sum = 0;
  for (const t of ["building", "ready", "sent", "responded", "interviewing",
                   "parked", "closed", "not-selected"]) {
    const n = Number(pill(d, t).querySelector(".n").textContent);
    ok(n === api.counts[t], `${t} pill says ${n}, the API says ${api.counts[t]}`);
    sum += n;
  }
  ok(sum === total, `the tabs account for every row — ${sum} of ${total}`);
  const readyN = api.counts.ready;
  ok(d.title.startsWith(`${readyN} ready · unsent ·`),
     `the title still leads with ready-and-unsent — got "${d.title}"`);

  console.log("\n3. Clicking a pill filters, as before");
  pill(d, "ready").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
  ok(visible(d).length === readyN, `ready shows ${visible(d).length}, expected ${readyN}`);
  ok(visible(d).every(r => r.dataset.status === "ready"), "and shows only ready rows");
  ok(pill(d, "ready").getAttribute("aria-current") === "true", "the pill marks itself current");
  pill(d, "all").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
  ok(visible(d).length === total, "back to all");

  console.log("\n4. Search filters on company and role");
  const probe = api.applications[0].company.split(" ")[0].toLowerCase();
  await type(w, probe);
  const hits = visible(d);
  ok(hits.length > 0 && hits.length < total, `"${probe}" narrows the list to ${hits.length}`);
  ok(hits.every(r => r.dataset.search.toLowerCase().includes(probe)), "every hit really matches");
  await type(w, "zzzznotacompany");
  ok(visible(d).length === 0, "a miss shows nothing");
  ok(!d.getElementById("tab-empty").hidden, "and says so");
  await type(w, "");
  ok(visible(d).length === total, "clearing the box restores every row");

  console.log("\n5. Search and tab compose, they do not fight");
  pill(d, "closed").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);
  await type(w, probe);
  ok(visible(d).every(r => r.dataset.status === "closed"
                           && r.dataset.search.toLowerCase().includes(probe)),
     "a filtered tab stays filtered while searching");
  await type(w, "");
  pill(d, "all").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(30);

  console.log("\n6. Both scores are visible, and nothing is invented");
  const scored = api.applications.find(a => a.technical != null);
  const card = [...rows(d)].find(r => r.dataset.search.includes(scored.slug));
  ok(card.querySelector(".app-score.tech").textContent.startsWith("technical "),
     "the technical score is on the card");
  ok(card.querySelector(".app-score.func"), "so is the non-technical one");
  const unscored = api.applications.find(a => a.technical == null);
  if (unscored) {
    const u = [...rows(d)].find(r => r.dataset.search.includes(unscored.slug));
    ok(u.querySelector(".app-score.tech").textContent === "technical —",
       "an unscored seat reads as a dash, never a number");
  } else ok(true, "no unscored seat to check");
  ok(rows(d).every(r => r.querySelector(".app-score.tech") && r.querySelector(".app-score.func")),
     "every row carries both badges");

  console.log("\n7. Compensation never reaches the page");
  ok(!/salary|₹|lacs|lpa/i.test(d.getElementById("app-list").textContent),
     "no compensation on any card — it is deferred");

  console.log("\n8. Plain http.server — says so, does not render an empty list");
  w = await boot(PLAIN); d = w.document;
  const s = d.getElementById("app-status");
  ok(!s.hidden && s.className.includes("bad"), "the page reports the failure");
  ok(s.textContent.includes("serve.py"), "and says how to fix it");
  ok(rows(d).length === 0, "no rows rendered");
  ok(d.getElementById("tab-empty").hidden,
     "and it does NOT say \"no applications match\" — that would be a lie");

  console.log("\n9. Database unreachable — 503, and the page still renders");
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
