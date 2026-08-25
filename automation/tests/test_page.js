const fs = require("fs"), { JSDOM } = require("jsdom");
const REPO = require("path").resolve(__dirname, "../..");
const API = "http://127.0.0.1:8106", PLAIN = "http://127.0.0.1:8107";
let P = 0, F = 0;
const ok = (c, l) => { c ? P++ : F++; console.log(`  ${c ? "PASS" : "FAIL"}  ${l}`); };
const settle = (ms = 90) => new Promise(r => setTimeout(r, ms));

async function boot(base) {
  const html = fs.readFileSync(REPO + "/daily/index.html", "utf8");
  const js = fs.readFileSync(REPO + "/static/todo.js", "utf8");
  const dom = new JSDOM(html, { url: base + "/daily/", runScripts: "outside-only" });
  const w = dom.window;
  // jsdom has no fetch; hand it Node's, resolving relative paths at `base`.
  w.fetch = (u, o) => fetch(u.startsWith("http") ? u : base + u, o);
  w.eval(js);
  // Do NOT dispatch DOMContentLoaded by hand: jsdom fires it itself once
  // parsing finishes, and dispatching too made the boot handler run twice.
  await new Promise(res => {
    if (w.document.readyState !== "loading") return res();
    w.document.addEventListener("DOMContentLoaded", res, { once: true });
    setTimeout(res, 2000);
  });
  await settle(250);
  return w;
}
const li  = (d, id) => d.querySelector(`.dl-day.today li[data-id="${id}"]`);
const tick = async (w, id, on = true) => {
  const b = li(w.document, id).querySelector("input");
  b.checked = on; b.dispatchEvent(new w.Event("change")); await settle();
};
const openMove = async (w, id, action) => {
  li(w.document, id).querySelector(`.dl-act[data-act="${action}"]`)
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle(40);
};
const confirmMove = async w => {
  w.document.getElementById("move-confirm").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
};
const move = async (w, id, action, reasons, note, until) => {
  await openMove(w, id, action);
  reasons.forEach(k => { w.document.querySelector(`#move-reasons input[value="${k}"]`).checked = true; });
  w.document.getElementById("move-note").value = note || "";
  if (until) w.document.getElementById("move-until").value = until;
  await confirmMove(w);
};

(async () => {
  await fetch(API + "/api/ops", { method: "POST", body: JSON.stringify({ ops: [] }) }).catch(() => {});

  console.log("\n1. Database mode");
  let w = await boot(API), d = w.document;
  ok(d.getElementById("store-banner").className.includes("ok"), "banner reports it is saving");
  ok(d.getElementById("store-banner").textContent.includes("PostgreSQL"), "banner names the store");
  ok(li(d, "clone-card").querySelector(".dl-due").textContent === "due today", "due-today badge");
  ok(li(d, "verify-dates").classList.contains("waiting"), "dependency gating still on");

  console.log("\n2. A tick reaches the database");
  await tick(w, "clone-card");
  const st = await (await fetch(API + "/api/state")).json();
  ok(st.tasks["2026-08-25::clone-card"]?.done === true, "row written to postgres");
  ok(!li(d, "verify-dates").classList.contains("waiting"), "dependant unlocked in the page");
  ok(!li(d, "clone-card").querySelector(".dl-due"), "a done task drops its due badge");

  console.log("\n3. Park with a reason");
  await move(w, "paste-jds", "parked", ["posting-closed", "comp-below"],
             "req pulled, and the band caps below floor");
  const parked = d.getElementById("moved-parked");
  ok(!parked.hidden, "Parked group appears");
  ok(parked.querySelector('li[data-id="paste-jds"]'), "the task moved into it");
  ok(parked.querySelector(".n").textContent === "1", "count is 1");
  ok(d.querySelector('.dl-group.parallel li[data-id="paste-jds"]') === null, "gone from the active list");
  const note = parked.querySelector(".dl-movednote").textContent;
  ok(note.includes("Posting no longer active") && note.includes("Comp band below the floor"),
     `BOTH reasons shown by label — "${note.slice(0, 70)}"`);
  ok(note.includes("band caps below floor"), "note shown alongside them");
  ok(parked.querySelector(".dl-revivable").textContent === "closed for good",
     "two terminal reasons => closed for good");
  // Denominator = today's ACTIVE tasks. Rolled-over tasks count too, so derive
  // the expectation rather than hardcoding it for the single-day case.
  const active = d.querySelectorAll(".dl-day.today .dl-group:not(.rolled) li[data-id], .dl-day.today .dl-group.rolled li[data-id]").length;
  ok(d.querySelector(".dl-count").textContent === `1/${active} done`,
     `parked task left the denominator — got "${d.querySelector('.dl-count').textContent}", ${active} active`);

  console.log("\n4. Push to a later day");
  await move(w, "source-ic", "pushed", ["blocked"], "", "2026-09-01");
  const pushed = d.getElementById("moved-pushed");
  ok(!pushed.hidden && pushed.querySelector('li[data-id="source-ic"]'), "task moved to Pushed");
  ok(pushed.querySelector(".dl-movednote").textContent.includes("until 2026-09-01"), "return date shown");
  ok(pushed.querySelector(".dl-revivable").textContent === "can come back",
     "a revivable reason => can come back");

  console.log("\n5. Drop, then restore");
  await move(w, "paste-11-15", "dropped", ["duplicate"], "");
  ok(!d.getElementById("moved-dropped").hidden, "Dropped group appears");
  li(d, "paste-11-15").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  ok(d.getElementById("moved-dropped").hidden, "Dropped group empties again");
  ok(d.querySelector('.dl-group.blocking li[data-id="paste-11-15"]'), "restored to its original group");

  console.log("\n5b. Confirming with no reason is refused");
  await openMove(w, "personal-info", "parked");
  await confirmMove(w);
  ok(!d.getElementById("move-hint").hidden, "the dialog says pick at least one reason");
  ok(!li(d, "personal-info").classList.contains("moved"), "and the task did NOT move");
  const stNo = await (await fetch(API + "/api/state")).json();
  ok(!stNo.tasks["2026-08-25::personal-info"], "nothing written to the database");
  d.querySelector('#move-reasons input[value="blocked"]').checked = true;
  await confirmMove(w);
  ok(li(d, "personal-info").classList.contains("moved"), "and it moves once a reason is picked");
  li(d, "personal-info").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();

  console.log("\n6. State survives a reload — the whole point of the database");
  w = await boot(API); d = w.document;
  ok(li(d, "clone-card").querySelector("input").checked, "tick came back from postgres");
  ok(d.getElementById("moved-parked").querySelector('li[data-id="paste-jds"]'), "park came back");
  ok(d.getElementById("moved-pushed").querySelector('li[data-id="source-ic"]'), "push came back");
  ok(d.getElementById("moved-dropped").hidden, "the restore stuck");

  console.log("\n7. History recorded every move");
  const h = (await (await fetch(API + "/api/history?limit=20")).json()).events;
  const acts = h.map(e => e.action);
  // 5b parks a second task, so count by key rather than by action alone.
  ok(h.filter(e => e.action === "parked" && e.key.endsWith("paste-jds")).length === 1,
     "exactly one park recorded for paste-jds");
  ok(acts.includes("restored") && acts.includes("dropped"), "drop AND its restore both kept");
  ok(JSON.stringify(h.find(e => e.action === "parked" && e.key.endsWith("paste-jds")).reasons) ===
     JSON.stringify(["posting-closed", "comp-below"]), "every reason persisted to history, in order");

  console.log("\n8. Plain http.server — degrades, does not break");
  w = await boot(PLAIN); d = w.document;
  ok(d.getElementById("store-banner").className.includes("warn"), "banner warns it is not saving");
  ok(d.getElementById("store-banner").textContent.includes("serve.py"), "banner says how to fix it");
  ok(!li(d, "clone-card").querySelector("input").checked, "does not see the database state");
  await tick(w, "clone-card");
  ok(li(d, "clone-card").classList.contains("done"), "ticking still works locally");
  ok(JSON.parse(w.localStorage.getItem("v2-daily-todo"))["2026-08-25::clone-card"].done === true,
     "fell back to localStorage");

  console.log("\n9. Rollover (needs a second day, added by the caller)");
  if (fs.readFileSync(REPO + "/daily/index.html", "utf8").includes('data-day="2026-08-24"')) {
    await fetch(API + "/api/ops", { method: "POST", body: JSON.stringify({ ops: [
      { key: "2026-08-24::old-done", action: "done" },
      { key: "2026-08-24::old-parked", action: "parked", reasons: ["posting-closed"] },
    ]})});
    w = await boot(API); d = w.document;
    const rolled = d.getElementById("rolled-over");
    const ids = [...rolled.querySelectorAll(".dl-list > li")].map(x => x.dataset.id);
    ok(!rolled.hidden, "rolled-over group shown");
    ok(ids.join(",") === "old-open,old-blocked", `only unfinished, unmoved tasks roll — got ${ids}`);
    ok(!ids.includes("old-done"), "a finished task does not roll over");
    ok(!ids.includes("old-parked"), "a PARKED task does not roll over either");
    const due = rolled.querySelector('li[data-id="old-open"] .dl-due');
    ok(due && due.textContent.includes("overdue"), `rolled task reads as overdue — got "${due && due.textContent}"`);
    ok(rolled.querySelector(".dl-from").textContent.includes("2026-08-24"), "shows the day it came from");
    const box = rolled.querySelector('li[data-id="old-open"] input');
    box.checked = true; box.dispatchEvent(new w.Event("change")); await settle();
    const origin = d.querySelector('.dl-day[data-day="2026-08-24"] li[data-id="old-open"]');
    ok(origin.classList.contains("done"), "ticking the rolled copy ticks its original");
    const st2 = await (await fetch(API + "/api/state")).json();
    ok(st2.tasks["2026-08-24::old-open"].done === true, "and it reached the database once");
  } else {
    console.log("  SKIP  (single-day log — caller did not add the synthetic day)");
  }

  console.log(`\n${P} passed, ${F} failed`);
  process.exit(F ? 1 : 0);
})();
