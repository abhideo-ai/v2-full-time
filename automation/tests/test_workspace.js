// The workspace page, end to end: a workspace's index.html shell + static/page-tabs.js
// + static/copy.js + static/workspace.js, against a real serve.py and a real
// jobs_tracker_v2. The pilot workspace is Delta's.
//
//   node automation/tests/test_workspace.js http://127.0.0.1:8006
//
// Read-only: it fetches pages and /api/jobs?slug=, and writes nothing. A test that
// needs a file that is not on disk (a broken manifest, a tab with a copy button)
// feeds it through `swap`, so no fixture is ever written into a workspace.
const fs = require("fs"), path = require("path"), { JSDOM, VirtualConsole } = require("jsdom");
const REPO = path.resolve(__dirname, "../..");
const API = process.argv[2];
const WS = "September-2026/27/delta-technology-referral";
const BASE = `/${WS}/`;
const TABS = [["overview", "Overview", "overview.html"], ["jd", "Job description", "jd.html"],
  ["score", "Tech score gaps", "score.html"], ["resume", "Résumé changes", null],
  ["research", "Research", "research.html"], ["kim", "Kim", "kim.html"],
  ["enhansd", "Enhansd", "enhansd.html"], ["questions", "Open questions", "questions.html"]];
const FILES = TABS.filter(([, , src]) => src && fs.existsSync(path.join(REPO, WS, src)));
let P = 0, F = 0;
const ok = (c, l) => { c ? P++ : F++; console.log(`  ${c ? "PASS" : "FAIL"}  ${l}`); };
const settle = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(cond, ms = 3000) {
  for (const end = Date.now() + ms; Date.now() < end; await settle(20)) if (cond()) return true;
  return false;
}

// Boot the shell the way a browser would: its own URL, relative fetches resolved
// against it, the three scripts in the shell's order. `swap` maps a path to
// [body, init] and answers for it instead of the server.
//
// ⚠ Every boot that swaps no tab file asserts that EVERY tab file loaded. Without
// it, a tab that failed to load passed as "no folds" and "no duplicate ids": that
// hid a planted duplicate id while serve.py's listen backlog (5) was resetting the
// eighth parallel request.
async function boot({ hash = "", swap = {} } = {}) {
  const url = `${API}${BASE}index.html${hash}`;
  const errors = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => errors.push(e.message));
  const dom = new JSDOM(await (await fetch(url)).text(), { url, runScripts: "outside-only", virtualConsole: vc });
  const w = dom.window;
  w.Element.prototype.scrollIntoView = function () { this.dataset.scrolledTo = "1"; }; // no layout in jsdom
  w.fetch = async (u) => {
    const abs = new URL(String(u), w.location.href);
    if (abs.pathname + abs.search in swap) return new Response(...swap[abs.pathname + abs.search]);
    if (abs.pathname in swap) return new Response(...swap[abs.pathname]);
    return fetch(abs.href);
  };
  for (const f of ["static/page-tabs.js", "static/copy.js", "static/workspace.js"])
    w.eval(fs.readFileSync(path.join(REPO, f), "utf8"));
  const d = w.document;
  await until(() => d.querySelector(".status-tab.active") || !d.getElementById("ws-error").hidden);
  await until(() => d.querySelectorAll("#ws-status .pill").length > 0);
  if (!Object.keys(swap).some((k) => k.startsWith(BASE))) {
    const empty = FILES.filter(([id]) => !d.getElementById(id) ||
      d.getElementById(id).textContent.trim().startsWith("Nothing here yet"));
    ok(empty.length === 0, `boot${hash ? " " + hash : ""}: all ${FILES.length} tab files loaded` +
       (empty.length ? ` — empty: ${empty.map(([id]) => d.getElementById(id)?.textContent.trim())}` : ""));
  }
  return { w, d, errors };
}
const labels = (d) => [...d.querySelectorAll("[data-page-tabs] .status-tab")].map((t) => t.textContent);
const active = (d) => d.querySelector(".status-tab.active")?.dataset.panel;
const shown = (d) => [...d.querySelectorAll("section[data-panel]")].filter((p) => !p.hidden).map((p) => p.id);

(async () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(REPO, WS, "workspace.json"), "utf8"));
  const seat = (await (await fetch(`${API}/api/jobs?slug=${manifest.slug}`)).json()).applications[0];

  console.log("\n1. The shell is the template, and holds nothing about any job");
  const shell = fs.readFileSync(path.join(REPO, WS, "index.html"), "utf8");
  ok(shell === fs.readFileSync(path.join(REPO, "templates/workspace/index.html"), "utf8"),
     "Delta's index.html is byte-identical to templates/workspace/index.html");
  ok(!/Delta|Enhansd|Kim/.test(shell), "and names no company, role or person");
  for (const f of ["index.html", "workspace.json", ...FILES.map(([, , s]) => s)]) {
    const r = await fetch(`${API}${BASE}${f}`);
    ok(r.status === 200, `${f} answers 200`);
  }
  ok((await fetch(`${API}/static/workspace.js`)).status === 200, "static/workspace.js answers 200");

  console.log("\n2. Six static tabs in order, this job's own tabs right after Research");
  let { w, d, errors } = await boot();
  ok(JSON.stringify(labels(d)) === JSON.stringify(TABS.map(([, l]) => l)),
     `tabs read ${labels(d).join(" · ")}`);
  ok(TABS.every(([id]) => d.querySelector(`section[data-panel="${id}"]#${id}`)),
     "every tab has its panel, id = name");
  ok(active(d) === "overview" && JSON.stringify(shown(d)) === '["overview"]',
     "Overview opens, and only its panel shows");
  ok(errors.length === 0, `no script errors — ${errors.join("; ") || "none"}`);

  console.log("\n3. Every tab shows exactly its own file's <main>, minus the standalone parts");
  for (const [id, , src] of FILES) {
    const file = new JSDOM(fs.readFileSync(path.join(REPO, WS, src), "utf8")).window.document;
    const main = file.querySelector("main");
    ok(file.querySelectorAll("main").length === 1, `${src} has one <main>`);
    ok(main.querySelector("[data-standalone]"), `${src} carries its own breadcrumb and title for opening on its own`);
    main.querySelectorAll("[data-standalone]").forEach((n) => n.remove());
    const norm = (s) => s.replace(/\s+/g, " ").trim();
    ok(norm(d.getElementById(id).textContent) === norm(main.textContent),
       `the ${id} tab is ${src}, word for word`);
  }
  ok(d.querySelectorAll("#ws-panels [data-standalone]").length === 0, "no standalone part reaches a tab");
  ok(d.querySelectorAll("h1").length === 1 && d.querySelectorAll(".breadcrumb").length === 1,
     "one title and one breadcrumb on the page: the shell's");

  console.log("\n4. A missing file is an empty state, never a missing tab");
  ok(d.getElementById("score").textContent.trim() === "Nothing here yet: score.html has not been written.",
     `score: "${d.getElementById("score").textContent.trim()}"`);
  ok(d.getElementById("resume").textContent.trim() === "Nothing here yet: workspace.json names no file for this tab.",
     `résumé changes: "${d.getElementById("resume").textContent.trim()}"`);
  const extra = { ...manifest, tabs: [...manifest.tabs, { id: "later", label: "Later", src: "later.html" },
    { id: "broken", label: "Broken", src: "broken.html" }] };
  ({ w, d, errors } = await boot({ swap: { [`${BASE}workspace.json`]: [JSON.stringify(extra)],
    [`${BASE}broken.html`]: ["", { status: 500 }] } }));
  ok(labels(d).slice(4, 9).join(" · ") === "Research · Kim · Enhansd · Later · Broken",
     "tabs added to workspace.json appear after Research, in the order written");
  ok(d.getElementById("later").textContent.trim() === "Nothing here yet: later.html has not been written.",
     "a tab whose file does not exist says so");
  ok(d.getElementById("broken").textContent.includes("could not be loaded (HTTP 500)"),
     "a file the server fails on says that instead");
  ok(d.getElementById("research").textContent.includes("2. The verdict"), "and the other tabs still load");

  console.log("\n5. The contract: no styles, no scripts, ids unique across every file");
  ({ w, d, errors } = await boot());
  for (const [, , src] of FILES) {
    const raw = fs.readFileSync(path.join(REPO, WS, src), "utf8");
    ok(!/<style/i.test(raw), `${src} has no <style>`);
    const scripts = raw.match(/<script[^>]*>/gi) || [];
    ok(scripts.every((s) => /src="(\.\.\/)*static\/copy\.js"/.test(s)) &&
       !/<script/i.test(raw.split("</main>")[0]), `${src} has no script of its own`);
  }
  ok(!/<style/i.test(shell), "nor does the shell");
  const ids = [...d.querySelectorAll("[id]")].map((n) => n.id);
  const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
  ok(dupes.length === 0, `every id is unique on the assembled page — ${ids.length} ids${dupes.length ? ", twice: " + dupes : ""}`);

  console.log("\n6. Folds: native <details>, the first in each tab open");
  for (const [id, , src] of FILES) {
    const folds = [...d.getElementById(id).querySelectorAll("details")];
    const inFile = (fs.readFileSync(path.join(REPO, WS, src), "utf8").match(/<details[\s>]/g) || []).length;
    ok(folds.length === inFile, `${id}: all ${inFile} of ${src}'s folds are in the tab`);
    if (!folds.length) continue;
    ok(folds[0].open && folds.slice(1).every((f) => !f.open), `${id}: ${folds.length} folds, the first open`);
    ok(folds.every((f) => f.firstElementChild.tagName === "SUMMARY" && f.lastElementChild.tagName === "DIV"),
       `${id}: every fold is <summary> + <div>`);
  }

  console.log("\n7. Links between tabs stay on this page, and every one lands");
  const tabFiles = TABS.filter(([, , s]) => s).map(([, , s]) => s);
  const links = [...d.querySelectorAll("#ws-panels a[href]")];
  ok(!links.some((a) => tabFiles.includes(a.getAttribute("href").split("#")[0])),
     "no link inside a tab points at another tab's file");
  const inPage = links.filter((a) => a.getAttribute("href").startsWith("#"));
  const dead = inPage.filter((a) => !d.getElementById(a.getAttribute("href").slice(1)));
  ok(inPage.length > 0 && dead.length === 0,
     `${inPage.length} in-page links, all landing${dead.length ? " — dead: " + dead.map((a) => a.getAttribute("href")) : ""}`);
  const verdictToKim = [...d.querySelectorAll("#verdict a")].find((a) => a.textContent === "section 4");
  ok(verdictToKim && verdictToKim.getAttribute("href") === "#kim-record",
     "research's \"section 4\" now points at the Kim tab (#kim-record)");
  w.location.hash = "#kim-record";
  w.dispatchEvent(new w.HashChangeEvent("hashchange"));
  await settle(30);
  ok(active(d) === "kim" && d.getElementById("kim-record").dataset.scrolledTo === "1",
     "following it opens the Kim tab and scrolls to section 4");

  console.log("\n8. The address picks the tab, and opens the fold it names");
  for (const [hash, tab] of [["#questions", "questions"], ["#research", "research"], ["#nonsense", "overview"]]) {
    ({ w, d, errors } = await boot({ hash }));
    ok(active(d) === tab && JSON.stringify(shown(d)) === JSON.stringify([tab]), `${hash} opens ${tab}`);
  }
  ({ w, d, errors } = await boot({ hash: "#flags" }));
  ok(active(d) === "research" && d.getElementById("flags").open && d.getElementById("flags").dataset.scrolledTo === "1",
     "#flags opens Research, opens the flags fold, and scrolls to it");
  ({ w, d, errors } = await boot({ hash: "#forcing-questions" }));
  ok(active(d) === "questions" && d.getElementById("forcing-questions").open,
     "#forcing-questions opens Open questions and that fold");

  console.log("\n9. The header comes from workspace.json and the tracker, not from hand-written pills");
  ({ w, d, errors } = await boot());
  ok(d.querySelector("h1").textContent === manifest.company, `h1: ${d.querySelector("h1").textContent}`);
  ok(d.getElementById("ws-role").textContent === "Role to be created · referral",
     `role line: ${d.getElementById("ws-role").textContent}`);
  ok(d.title === `${manifest.company} · ${manifest.role}`, `title: ${d.title}`);
  const crumbs = [...d.querySelectorAll("#ws-crumbs a")].map((a) => a.getAttribute("href"));
  ok(JSON.stringify(crumbs) === JSON.stringify(["../../../index.html", "../../../index.html?month=2026-09",
    "../../../index.html?date=2026-09-27", "../../../index.html?q=delta-technology-referral"]),
     "the breadcrumb filters the launcher by month, day and seat");
  ok(d.getElementById("ws-crumbs").textContent ===
     "Full-time JD (job description) workspace › September-2026 › 27 › delta-technology-referral",
     `breadcrumb reads: ${d.getElementById("ws-crumbs").textContent}`);
  const pills = [...d.querySelectorAll("#ws-status .pill")].map((p) => p.textContent);
  ok(pills[0] === `tracker: ${seat.status.replace(/_/g, " ")}`, `status pill is the database's — "${pills[0]}"`);
  ok(pills[1] === (seat.technical == null ? "not scored" : `technical ${seat.technical}`),
     `score pill is the database's — "${pills[1]}"`);

  console.log("\n10. The tracker unreachable: the header says so, and the tabs still render");
  ({ w, d, errors } = await boot({ swap: { [`/api/jobs?slug=${manifest.slug}`]: ["{}", { status: 503 }] } }));
  ok(d.querySelector("#ws-status .pill.warn")?.textContent === "tracker unavailable (HTTP 503)",
     "a warning pill names the status it got");
  ok(d.getElementById("research").textContent.includes("2. The verdict"), "and every tab still loads");

  console.log("\n11. A copy button inside a tab works (copy.js is the shell's)");
  const block = '<main><div class="copy-block copy-target" id="copy-test"><button class="copy-btn" ' +
    'data-copy-target="#copy-test">Copy</button><p>Paste <strong>me</strong></p></div></main>';
  ({ w, d, errors } = await boot({ swap: { [`${BASE}score.html`]: [block] } }));
  let copied = null;
  Object.defineProperty(w.navigator, "clipboard", { value: { writeText: async (t) => { copied = t; } } });
  d.querySelector("#score .copy-btn").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await until(() => copied !== null);
  ok(copied === "Paste me", `the click reached copy.js and copied "${copied}"`);

  console.log("\n12. Printing opens every fold, and puts them back afterwards");
  ({ w, d, errors } = await boot());
  const closed = [...d.querySelectorAll("details")].filter((x) => !x.open).length;
  w.dispatchEvent(new w.Event("beforeprint"));
  ok(closed > 0 && [...d.querySelectorAll("details")].every((x) => x.open), `all ${closed} closed folds open to print`);
  w.dispatchEvent(new w.Event("afterprint"));
  ok([...d.querySelectorAll("details")].filter((x) => !x.open).length === closed, "and close again after");

  console.log("\n13. A broken manifest is reported, never a blank page");
  ({ w, d, errors } = await boot({ swap: { [`${BASE}workspace.json`]: ["", { status: 404 }] } }));
  ok(!d.getElementById("ws-error").hidden &&
     d.getElementById("ws-error").textContent.includes("workspace.json has not been written") &&
     d.getElementById("ws-error").textContent.includes("serve.py"),
     "no workspace.json: the page says so, and how to open it");
  const twice = { ...manifest, tabs: [{ id: "research", label: "Again", src: "x.html" }] };
  ({ w, d, errors } = await boot({ swap: { [`${BASE}workspace.json`]: [JSON.stringify(twice)] } }));
  ok(d.getElementById("ws-error").textContent.includes('the tab id "research" twice'),
     "a tab id used twice is named, not rendered as two tabs");

  console.log("\n14. The template's example tab files obey the same contract");
  const TPL = path.join(REPO, "templates/workspace");
  const tplFiles = fs.readdirSync(TPL).filter((f) => f.endsWith(".html") && f !== "index.html");
  ok(tplFiles.length === 6, `one example per static tab — ${tplFiles.join(", ")}`);
  const tplIds = [];
  for (const f of tplFiles) {
    const raw = fs.readFileSync(path.join(TPL, f), "utf8");
    const doc = new JSDOM(raw).window.document;
    ok(doc.querySelectorAll("main").length === 1 && doc.querySelector("main [data-standalone]") &&
       !/<style/i.test(raw) && !/<script/i.test(raw.split("</main>")[0]) &&
       (raw.match(/<script[^>]*>/gi) || []).every((s) => /src="(\.\.\/)*static\/copy\.js"/.test(s)),
       `${f}: one <main>, a standalone masthead, no style, no script of its own`);
    tplIds.push(...[...doc.querySelectorAll("main [id]")].map((n) => n.id));
  }
  ok(tplIds.every((id, i) => tplIds.indexOf(id) === i) && !tplIds.some((id) => TABS.some(([t]) => t === id)),
     `their ${tplIds.length} ids are unique across the files, and none is a tab's name`);
  const tplManifest = JSON.parse(fs.readFileSync(path.join(TPL, "workspace.json"), "utf8"));
  ok(JSON.stringify(Object.keys(tplManifest)) === JSON.stringify(Object.keys(manifest)),
     "its workspace.json has exactly the keys Delta's has");

  console.log(`\n${P} passed, ${F} failed`);
  process.exit(F ? 1 : 0);
})();
