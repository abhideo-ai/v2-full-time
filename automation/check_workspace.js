// Check one workspace against the tab-file contract (static/workspace.js's header):
// the deterministic half of a seat's verify pass. Read-only: it reads files and the
// running server, and writes nothing.
//
//   node automation/check_workspace.js September-2026/28/<slug> [http://127.0.0.1:8006]
//
// FAIL lines break the contract and exit 1. WARN lines need a human look (a word that
// can mean compensation, an empty tab). test_workspace.js tests the mechanism on Delta;
// this checks any workspace's content.
const fs = require("fs"), path = require("path"), { JSDOM, VirtualConsole } = require("jsdom");
const REPO = path.resolve(__dirname, "..");
const [WS, API = "http://127.0.0.1:8006"] = process.argv.slice(2);
if (!WS) { console.error("usage: node automation/check_workspace.js <Month-YYYY/DD/slug> [server]"); process.exit(2); }
const DIR = path.join(REPO, WS);
const STATIC = ["overview.html", "jd.html", "score.html", "research.html", "questions.html"];
const TAB_IDS = ["overview", "jd", "score", "resume", "research", "questions"];
const PAY = /\b(salary|salaries|CTC|LPA|lakhs?|crores?|compensation|pay band|pay range)\b|₹/i;
let fails = 0, warns = 0;
const ok = (c, l) => { if (!c) fails++; console.log(`  ${c ? "PASS" : "FAIL"}  ${l}`); return c; };
const warn = (l) => { warns++; console.log(`  WARN  ${l}`); };
const settle = (ms) => new Promise((r) => setTimeout(r, ms));
const read = (f) => fs.readFileSync(path.join(DIR, f), "utf8");

(async () => {
  console.log(`\n${WS}\n\n1. Shell and manifest`);
  ok(read("index.html") === fs.readFileSync(path.join(REPO, "templates/workspace/index.html"), "utf8"),
     "index.html is the shell, byte for byte");
  let m;
  try { m = JSON.parse(read("workspace.json")); } catch (e) { ok(false, `workspace.json parses — ${e.message}`); process.exit(1); }
  ok(m.slug === path.basename(DIR), `slug is the folder's name — ${m.slug}`);
  const [month, day] = WS.split("/").slice(-3, -1);
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December"];
  const [y, mo, dd] = String(m.received).split("-");
  ok(/^\d{4}-\d{2}-\d{2}$/.test(m.received) && dd === day && month === `${MONTHS[mo - 1]}-${y}`,
     `received ${m.received} matches the folder ${month}/${day}`);
  ok(m.company && m.role && m.route, "company, role and route are filled in");
  ok(Array.isArray(m.tabs) && m.tabs.every((t) => t.id && t.label && t.src && !TAB_IDS.includes(t.id)),
     `this job's own tabs are complete and reuse no static tab's id — ${m.tabs.map((t) => t.id).join(", ") || "none"}`);
  const srcs = [...STATIC, ...(m.resume_changes ? [m.resume_changes] : []), ...m.tabs.map((t) => t.src)];
  const present = srcs.filter((s) => fs.existsSync(path.join(DIR, s)));
  for (const s of srcs.filter((s) => !present.includes(s))) console.log(`  info  ${s} is not written; its tab says so`);

  console.log("\n2. Every tab file on its own");
  for (const f of present) {
    const raw = read(f);
    const doc = new JSDOM(raw).window.document;
    const main = doc.querySelectorAll("main");
    ok(main.length === 1 && main[0].querySelector("[data-standalone]"), `${f}: one <main>, with its own breadcrumb and title`);
    ok(!/<style/i.test(raw) && !/<script/i.test(raw.split("</main>")[0]) &&
       (raw.match(/<script[^>]*>/gi) || []).every((s) => /src="(\.\.\/)*static\/copy\.js"/.test(s)),
       `${f}: no style, no script of its own`);
    const left = raw.match(/\{\{[^}]*\}\}/g);
    ok(!left, `${f}: no template placeholder left${left ? " — " + left.slice(0, 3).join(" ") : ""}`);
    ok(!/<!--\s*TEMPLATE/.test(raw), `${f}: the template's comment is gone`);
    const folds = [...main[0].querySelectorAll("details")];
    if (folds.length) {
      ok(folds.every((d) => d.firstElementChild?.tagName === "SUMMARY" && d.lastElementChild?.tagName === "DIV"),
         `${f}: every fold is <summary> + <div>`);
      ok(folds[0].open && folds.slice(1).every((d) => !d.open), `${f}: ${folds.length} folds, the first open`);
    }
    if (f !== "jd.html") {
      const hits = (main[0].textContent.match(new RegExp(PAY.source, "gi")) || []);
      if (hits.length) warn(`${f}: mentions ${[...new Set(hits)].join(", ")} — never compensation; check the context`);
    }
  }

  console.log("\n3. The assembled page, from the running server");
  const url = `${API}/${WS}/index.html`;
  const errors = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => errors.push(e.message));
  let html;
  try { html = await (await fetch(url)).text(); } catch (e) { ok(false, `${url} answers — ${e.message}; is serve.py running?`); process.exit(1); }
  const w = new JSDOM(html, { url, runScripts: "outside-only", virtualConsole: vc }).window;
  w.Element.prototype.scrollIntoView = () => {};
  w.fetch = (u) => fetch(new URL(String(u), w.location.href).href);
  for (const f of ["static/page-tabs.js", "static/copy.js", "static/workspace.js"])
    w.eval(fs.readFileSync(path.join(REPO, f), "utf8"));
  const d = w.document;
  for (const end = Date.now() + 5000; Date.now() < end && !d.querySelector(".status-tab.active") &&
       d.getElementById("ws-error").hidden; ) await settle(20);
  for (const end = Date.now() + 3000; Date.now() < end && !d.querySelector("#ws-status .pill"); ) await settle(20);
  ok(d.getElementById("ws-error").hidden, `the page builds${d.getElementById("ws-error").hidden ? "" : " — " + d.getElementById("ws-error").textContent}`);
  const tabOf = new Map([...STATIC.map((s, i) => [s, ["overview", "jd", "score", "research", "questions"][i]]),
    ...(m.resume_changes ? [[m.resume_changes, "resume"]] : []), ...m.tabs.map((t) => [t.src, t.id])]);
  const empty = present.filter((s) => d.getElementById(tabOf.get(s))?.textContent.trim().startsWith("Nothing here yet"));
  ok(!empty.length, `all ${present.length} tab files load into their tabs${empty.length ? " — empty: " + empty : ""}`);
  ok(!d.querySelector("#ws-panels [data-standalone]") && d.querySelectorAll("h1").length === 1,
     "no standalone part reaches a tab; one title on the page");
  const ids = [...d.querySelectorAll("[id]")].map((n) => n.id);
  const twice = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
  ok(!twice.length, `${ids.length} ids, each used once${twice.length ? " — twice: " + twice : ""}`);
  const links = [...d.querySelectorAll("#ws-panels a[href]")];
  const toFiles = links.filter((a) => srcs.includes(a.getAttribute("href").split("#")[0]));
  ok(!toFiles.length, `no link leaves the page for another tab's file${toFiles.length ? " — " + toFiles.map((a) => a.getAttribute("href")) : ""}`);
  const dead = links.filter((a) => a.getAttribute("href").startsWith("#") && !d.getElementById(a.getAttribute("href").slice(1)));
  ok(!dead.length, `every in-page link lands${dead.length ? " — dead: " + [...new Set(dead.map((a) => a.getAttribute("href")))] : ""}`);
  const pill = d.querySelector("#ws-status .pill")?.textContent || "";
  ok(pill.startsWith("tracker: "), `the header reads the tracker — "${pill}"`);
  ok(!errors.length, `no script errors${errors.length ? " — " + errors.join("; ") : ""}`);

  console.log(`\n${fails ? "FAILED" : "PASSED"}: ${fails} failure(s), ${warns} warning(s)`);
  process.exit(fails ? 1 : 0);
})();
