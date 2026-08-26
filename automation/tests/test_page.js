// The daily board, end to end: real server, real PostgreSQL, real markup.
//
// What these assertions are FOR. The board's lanes are automation/db.py's
// states, so most of what can go wrong here is semantic rather than visual:
//
//   * the board must be dated TODAY, not "the newest day in days.json";
//   * a task must exist exactly ONCE in the page — rollover moves, never clones;
//   * a waiting task must stay in the Open lane, enabled and clickable;
//   * a move-out zone must stay visible when empty, or it stops being a target;
//   * and, above all, NOTHING may leave the board without a reason — by button,
//     by drag, or by keyboard. Three sections below attack that one rule from
//     three directions, because a silent reasonless park is the single worst
//     thing this page could ship.
const fs = require("fs"), { JSDOM } = require("jsdom");
const { execSync } = require("child_process");
const REPO = require("path").resolve(__dirname, "../..");
const API = "http://127.0.0.1:8106", PLAIN = "http://127.0.0.1:8107";
let P = 0, F = 0;
const ok = (c, l) => { c ? P++ : F++; console.log(`  ${c ? "PASS" : "FAIL"}  ${l}`); };
const settle = (ms = 90) => new Promise(r => setTimeout(r, ms));
// Parse the live title rather than hardcoding numbers: the runner adds a
// synthetic second day, so the totals differ between a one-day and two-day log.
const titleParts = d => {
  const m = d.title.match(/^(?:(\d+) overdue · )?(\d+)\/(\d+) · (.+)$/);
  return m ? { overdue: Number(m[1] || 0), done: Number(m[2]), total: Number(m[3]), stem: m[4] }
           : { raw: d.title };
};

const now = new Date();
const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const TODAY = iso(now);
const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const PRETTY_TODAY = `${WD[now.getDay()]} ${now.getDate()} ${MO[now.getMonth()]} ${now.getFullYear()}`;
const regenerate = () => execSync(`${REPO}/automation/.venv/bin/python automation/daily.py`,
                                 { cwd: REPO, stdio: "ignore" });

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
// One task is one node now, anywhere in the document — so this no longer needs
// scoping to a day, and section 9 proves the node really is unique.
const li = (d, id) => d.querySelector(`li[data-id="${id}"]`);
const lane = node => (node && node.parentNode && node.parentNode.dataset)
  ? node.parentNode.dataset.drop : null;
const inLane = (d, id) => lane(li(d, id));
const laneIds = (d, drop) =>
  [...d.querySelectorAll(`.kb-drop[data-drop="${drop}"] > li`)].map(x => x.dataset.id);
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
// A drag, as far as the page is concerned: pick the card up by its handle, let
// go over a lane. jsdom has no DragEvent, and it does not need one — the
// handlers keep the dragged entry in a closure precisely so the drop path is
// the same whether a mouse or a test dispatched it.
const drag = async (w, id, drop) => {
  const card = li(w.document, id);
  card.dispatchEvent(new w.Event("dragstart", { bubbles: true }));
  w.document.querySelector(`.kb-drop[data-drop="${drop}"]`)
    .dispatchEvent(new w.Event("drop", { bubbles: true }));
  card.dispatchEvent(new w.Event("dragend", { bubbles: true }));
  await settle();
};
const arrow = async (w, id, key) => {
  li(w.document, id).querySelector(".kb-grab")
    .dispatchEvent(new w.KeyboardEvent("keydown", { key, bubbles: true }));
  await settle();
};
const dbState = async () => (await (await fetch(API + "/api/state")).json()).tasks;

(async () => {
  await fetch(API + "/api/ops", { method: "POST", body: JSON.stringify({ ops: [] }) }).catch(() => {});
  const authoredToday = fs.readFileSync(REPO + "/daily/index.html", "utf8")
    .includes(`<details class="dl-day today" data-day="${TODAY}"`);

  console.log("\n1. The board is dated TODAY, not the newest day in days.json");
  let w = await boot(API), d = w.document;
  ok(d.getElementById("store-banner").className.includes("ok"), "banner reports it is saving");
  ok(d.getElementById("store-banner").textContent.includes("PostgreSQL"), "banner names the store");
  ok(d.getElementById("board").dataset.day === TODAY,
     `board carries today's date — got "${d.getElementById("board").dataset.day}", today is ${TODAY}`);
  ok(d.getElementById("board-date").textContent.trim() === PRETTY_TODAY,
     `board header reads today — got "${d.getElementById("board-date").textContent.trim()}"`);
  if (!authoredToday) {
    ok(!d.querySelector(`.dl-day[data-day="${TODAY}"]`),
       "nothing was authored for today — the defect case this dating fixes");
    ok(/Nothing was authored for today/.test(d.getElementById("board-rolled").textContent),
       `and the board says so — "${d.getElementById("board-rolled").textContent}"`);
    ok(!d.getElementById("board-rolled").hidden, "that note is visible, not just present");
  } else {
    console.log("  SKIP  (days.json happens to hold today — the no-entry path is not exercised)");
  }
  const due = li(d, "clone-card").querySelector(".dl-due");
  ok(due && /overdue$/.test(due.textContent),
     `a card from an earlier day reads overdue on today's board — got "${due && due.textContent}"`);
  ok(li(d, "clone-card").querySelector(".dl-from").textContent.includes("2026-08-25"),
     "and says which day it rolled from");

  console.log("\n1b. Lanes are db.py's states, and waiting is a sort — never a lock");
  ok(inLane(d, "clone-card") === "open", "an unfinished task is in the Open lane");
  ok(inLane(d, "verify-dates") === "open",
     "a WAITING task is in Open too — there is deliberately no Blocked lane");
  ok(li(d, "verify-dates").classList.contains("waiting"), "dependency gating still on");
  ok(li(d, "verify-dates").querySelector("input").disabled === false,
     "a waiting task's checkbox is NOT disabled — out-of-order work is legitimate");
  ok(li(d, "verify-dates").querySelectorAll('.dl-act:not([hidden])').length >= 3,
     "and it keeps its Park / Push / Drop buttons");
  const openIds = laneIds(d, "open");
  const firstWaiting = openIds.findIndex(id => li(d, id).classList.contains("waiting"));
  const lastReady = openIds.map(id => li(d, id).classList.contains("waiting")).lastIndexOf(false);
  ok(firstWaiting === -1 || firstWaiting > lastReady,
     `Open sorts ready before waiting — got ${openIds.join(",")}`);
  ok(d.querySelector("#lane-open .kb-n").textContent === String(openIds.length),
     `the Open count is re-derived from the rows in the lane — reads ${d.querySelector("#lane-open .kb-n").textContent}, ${openIds.length} rows`);
  ok(li(d, openIds[0]).classList.contains("kb-next"),
     "the top card of Open is the one Do next names");
  let T = titleParts(d);
  ok(T.done === 0 && T.total > 0, `live title leads with progress — got "${d.title}"`);
  ok(T.stem && T.stem.startsWith("Daily to-do"), "live title keeps the page name as its stem");

  console.log("\n2. A tick reaches the database and the card changes lane");
  await tick(w, "clone-card");
  ok((await dbState())["2026-08-25::clone-card"]?.done === true, "row written to postgres");
  ok(inLane(d, "clone-card") === "done", "and the card is now in the Done lane");
  ok(d.querySelector("#lane-done .kb-n").textContent === "1", "the Done count follows it");
  ok(!li(d, "verify-dates").classList.contains("waiting"), "dependant unlocked in the page");
  ok(!li(d, "clone-card").querySelector(".dl-due"), "a done task drops its due badge");
  ok(titleParts(d).done === 1, `title tracks the tick — got "${d.title}"`);

  console.log("\n3. Park with a reason — the button path");
  await move(w, "paste-jds", "parked", ["posting-closed", "comp-below"],
             "req pulled, and the band caps below floor");
  const parked = d.getElementById("moved-parked");
  ok(inLane(d, "paste-jds") === "parked", "the task moved into the Parked zone");
  ok(parked.querySelector(".n").textContent === "1", "count is 1");
  ok(!parked.classList.contains("empty"), "and the zone no longer reads empty");
  ok(!laneIds(d, "open").includes("paste-jds"), "gone from the Open lane");
  const note = parked.querySelector(".dl-movednote").textContent;
  ok(note.includes("Posting no longer active") && note.includes("Comp band below the floor"),
     `BOTH reasons shown by label — "${note.slice(0, 70)}"`);
  ok(note.includes("band caps below floor"), "note shown alongside them");
  ok(parked.querySelector(".dl-revivable").textContent === "closed for good",
     "two terminal reasons => closed for good");
  ok(!parked.querySelector(".dl-due"), "a parked card stops advertising a due date");
  // Denominator = what is on the board and not moved out.
  const active = d.querySelectorAll("#lane-open > .kb-drop > li, #lane-done > .kb-drop > li").length;
  ok(titleParts(d).total === active,
     `a parked task leaves the title's denominator too — title says ${titleParts(d).total}, ${active} on the board`);
  ok(d.getElementById("moved-dropped").hidden === false,
     "an EMPTY zone stays visible — a zone you cannot see is a zone you cannot drop onto");
  ok(d.getElementById("moved-dropped").classList.contains("empty"),
     "it is marked empty rather than hidden");

  console.log("\n4. Push is a timed lane — it empties itself");
  await move(w, "source-ic", "pushed", ["blocked"], "", "2026-09-01");
  const pushed = d.getElementById("moved-pushed");
  ok(inLane(d, "source-ic") === "pushed", "task moved to Pushed");
  ok(pushed.querySelector(".dl-movednote").textContent.includes("until 2026-09-01"), "return date shown");
  ok(pushed.querySelector(".dl-revivable").textContent === "can come back",
     "a revivable reason => can come back");
  const past = iso(new Date(now.getTime() - 86400000));
  await move(w, "personal-info", "pushed", ["blocked"], "", past);
  ok(inLane(d, "personal-info") === "open",
     `a push whose return date has passed is back in Open with no write — got ${inLane(d, "personal-info")}`);
  ok((await dbState())["2026-08-25::personal-info"].moved === "pushed",
     "the database still records the push; only the lane reads the clock");
  li(d, "personal-info").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();

  console.log("\n5. Drop, then restore");
  await move(w, "paste-11-15", "dropped", ["duplicate"], "");
  ok(d.getElementById("moved-dropped").querySelector(".n").textContent === "1", "Dropped zone counts it");
  li(d, "paste-11-15").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  ok(d.getElementById("moved-dropped").querySelector(".n").textContent === "0", "Dropped zone empties again");
  ok(d.getElementById("moved-dropped").classList.contains("empty") &&
     !d.getElementById("moved-dropped").hidden, "and stays on the board as a target");
  ok(inLane(d, "paste-11-15") === "open", "the restored task is back in Open");

  console.log("\n5b. THE REASON GATE — buttons");
  await openMove(w, "fix-el-paso", "parked");
  await confirmMove(w);
  ok(!d.getElementById("move-hint").hidden, "the dialog says pick at least one reason");
  ok(!li(d, "fix-el-paso").classList.contains("moved"), "and the task did NOT move");
  ok(inLane(d, "fix-el-paso") === "open", "it is still sitting in Open");
  ok(!(await dbState())["2026-08-25::fix-el-paso"], "nothing written to the database");
  d.querySelector('#move-reasons input[value="blocked"]').checked = true;
  await confirmMove(w);
  ok(inLane(d, "fix-el-paso") === "parked", "and it moves once a reason is picked");
  li(d, "fix-el-paso").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();

  console.log("\n5c. THE REASON GATE — a DRAG onto a move-out zone is a request, not a save");
  await drag(w, "first-export", "parked");
  ok(d.getElementById("move-dialog").hasAttribute("open") ||
     d.getElementById("move-dialog").open, "dropping on Parked opens the reason dialog");
  ok(inLane(d, "first-export") === "open",
     `the card did NOT move — an optimistic move is a reasonless park on screen (lane: ${inLane(d, "first-export")})`);
  ok(!(await dbState())["2026-08-25::first-export"], "and NOTHING was written to the database");
  d.getElementById("move-cancel").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  ok(inLane(d, "first-export") === "open", "cancelling leaves it exactly where it was");
  ok(!(await dbState())["2026-08-25::first-export"], "and still writes nothing");
  await drag(w, "first-export", "dropped");
  d.querySelector('#move-reasons input[value="jd-changed"]').checked = true;
  await confirmMove(w);
  ok(inLane(d, "first-export") === "dropped", "the same drag completes once a reason is given");
  const fe = (await dbState())["2026-08-25::first-export"];
  ok(fe && fe.moved === "dropped" && JSON.stringify(fe.reasons) === '["jd-changed"]',
     "and the drag wrote the same row `./todo drop` would — action plus reasons");

  console.log("\n5d. Keyboard parity — arrows take the identical path");
  await arrow(w, "journey-doc", "ArrowRight");
  ok(inLane(d, "journey-doc") === "done", "ArrowRight from Open ticks the card");
  ok((await dbState())["2026-08-25::journey-doc"].done === true, "through the same op");
  await arrow(w, "journey-doc", "ArrowRight");
  ok(d.getElementById("move-dialog").hasAttribute("open") ||
     d.getElementById("move-dialog").open, "ArrowRight into Parked asks for a reason, like a drop");
  ok(inLane(d, "journey-doc") === "done", "and moves nothing while it asks");
  d.getElementById("move-cancel").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  await arrow(w, "journey-doc", "ArrowLeft");
  ok(inLane(d, "journey-doc") === "open", "ArrowLeft unticks it again");
  ok(li(d, "journey-doc").querySelector(".kb-grab").getAttribute("aria-keyshortcuts")
     === "ArrowLeft ArrowRight", "the handle advertises those keys to a screen reader");

  console.log("\n6. State survives a reload — the whole point of the database");
  w = await boot(API); d = w.document;
  ok(li(d, "clone-card").querySelector("input").checked, "tick came back from postgres");
  ok(inLane(d, "clone-card") === "done", "and it came back in the Done lane");
  ok(inLane(d, "paste-jds") === "parked", "park came back");
  ok(inLane(d, "source-ic") === "pushed", "push came back");
  ok(inLane(d, "first-export") === "dropped", "the dragged drop came back");
  ok(inLane(d, "paste-11-15") === "open", "the restore stuck");

  console.log("\n7. History recorded every move");
  const h = (await (await fetch(API + "/api/history?limit=40")).json()).events;
  const acts = h.map(e => e.action);
  ok(h.filter(e => e.action === "parked" && e.key.endsWith("paste-jds")).length === 1,
     "exactly one park recorded for paste-jds");
  ok(acts.includes("restored") && acts.includes("dropped"), "drop AND its restore both kept");
  ok(JSON.stringify(h.find(e => e.action === "parked" && e.key.endsWith("paste-jds")).reasons) ===
     JSON.stringify(["posting-closed", "comp-below"]), "every reason persisted to history, in order");
  ok(h.some(e => e.action === "dropped" && e.key.endsWith("first-export")),
     "a drag lands in history as an ordinary op, indistinguishable from ./todo");

  console.log("\n8. Plain http.server — degrades, does not break");
  w = await boot(PLAIN); d = w.document;
  ok(d.getElementById("store-banner").className.includes("warn"), "banner warns it is not saving");
  ok(d.getElementById("store-banner").textContent.includes("serve.py"), "banner says how to fix it");
  ok(!li(d, "clone-card").querySelector("input").checked, "does not see the database state");
  ok(d.getElementById("board").dataset.day === TODAY, "and the board is still dated today");
  await tick(w, "clone-card");
  ok(inLane(d, "clone-card") === "done", "ticking still works locally");
  ok(JSON.parse(w.localStorage.getItem("v2-daily-todo"))["2026-08-25::clone-card"].done === true,
     "fell back to localStorage");
  await move(w, "paste-jds", "parked", ["posting-closed", "jd-changed"], "local park");
  const localNote = li(d, "paste-jds").querySelector(".dl-movednote").textContent;
  ok(inLane(d, "paste-jds") === "parked", "a local park moves the card too");
  ok(localNote.includes("Posting no longer active") && localNote.includes("JD changed materially"),
     `and the fallback keeps the reasons as a LIST — "${localNote.slice(0, 80)}"`);
  ok(li(d, "paste-jds").querySelector(".dl-revivable").textContent === "closed for good",
     "so revivability is computed from every reason, not from undefined");
  ok(JSON.stringify(JSON.parse(w.localStorage.getItem("v2-daily-todo"))["2026-08-25::paste-jds"].reasons)
     === '["posting-closed","jd-changed"]', "and localStorage stores the same shape the server does");

  console.log("\n9. Rollover MOVES a card; it never clones one");
  if (fs.readFileSync(REPO + "/daily/index.html", "utf8").includes('data-day="2026-08-24"')) {
    await fetch(API + "/api/ops", { method: "POST", body: JSON.stringify({ ops: [
      { key: "2026-08-24::old-done", action: "done" },
      { key: "2026-08-24::old-parked", action: "parked", reasons: ["posting-closed"] },
    ]})});
    w = await boot(API); d = w.document;
    const rolledIds = laneIds(d, "open").filter(id => id.startsWith("old-"));
    ok(rolledIds.join(",") === "old-open,old-blocked",
       `only unfinished, unmoved tasks roll into Open — got ${rolledIds}`);
    ok(inLane(d, "old-done") === "done",
       "a task finished TODAY shows in Done rather than rolling — otherwise the lane empties on refresh");
    ok(inLane(d, "old-parked") === "parked", "and one parked today shows in Parked");
    ok(d.querySelectorAll('li[data-id="old-open"]').length === 1,
       `ONE node for one task — the rolled card is moved, not cloned (found ${d.querySelectorAll('li[data-id="old-open"]').length})`);
    ok(d.querySelector('.dl-day[data-day="2026-08-24"] li[data-id="old-open"]') === null,
       "so it is no longer sitting in its origin day's list");
    // The invariant that proves move-not-clone without depending on which tasks
    // happen to have been touched in this run.
    const dayEl = d.querySelector('.dl-day[data-day="2026-08-24"]');
    const left = dayEl.querySelectorAll("li[data-id]").length;
    const onBoard = [...d.querySelectorAll(".kb-drop > li")]
      .filter(x => x.dataset.day === "2026-08-24").length;
    ok(left + onBoard === 4,
       `every authored task is in exactly one place — ${onBoard} on the board + ${left} left in the day = 4`);
    ok(dayEl.querySelector(".dl-onboard").textContent === `${onBoard} on the board`,
       `and the day summary says so — got "${dayEl.querySelector(".dl-onboard").textContent}"`);
    const oDue = li(d, "old-open").querySelector(".dl-due");
    ok(oDue && oDue.textContent.includes("overdue"), `rolled task reads as overdue — got "${oDue && oDue.textContent}"`);
    ok(li(d, "old-open").querySelector(".dl-from").textContent.includes("2026-08-24"), "shows the day it came from");
    ok(/^\d+ overdue · /.test(d.title), `overdue count leads the title — got "${d.title}"`);
    const box = li(d, "old-open").querySelector("input");
    box.checked = true; box.dispatchEvent(new w.Event("change")); await settle();
    ok((await dbState())["2026-08-24::old-open"].done === true,
       "ticking it writes against its ORIGIN day's key, not today's");
    ok(inLane(d, "old-open") === "done", "and the one node moves to Done");
    ok(!li(d, "old-blocked").classList.contains("waiting"),
       "unblocking a rolled dependency resolves against its own day, not today");
  } else {
    console.log("  SKIP  (single-day log — caller did not add the synthetic day)");
  }

  console.log("\n10. A day authored FOR today — the other half of the dating fix");
  const daysPath = REPO + "/daily/days.json";
  const doc = JSON.parse(fs.readFileSync(daysPath, "utf8"));
  doc.days.push({ date: TODAY, groups: [{ title: "Authored for today", kind: "parallel",
    why: "synthetic test day", items: [
      { id: "today-open", p: 1, needs: [], task: "Due today", detail: "" },
      { id: "today-blocked", p: 2, needs: ["today-open"], task: "Blocked today", detail: "" }] }] });
  fs.writeFileSync(daysPath, JSON.stringify(doc, null, 2) + "\n");
  regenerate();
  w = await boot(API); d = w.document;
  ok(d.getElementById("board-date").textContent.trim() === PRETTY_TODAY,
     "the board header still reads today when today IS authored");
  ok(li(d, "today-open").querySelector(".dl-due").textContent === "due today",
     `a task authored for today reads "due today" — got "${li(d, "today-open").querySelector(".dl-due").textContent}"`);
  ok(!li(d, "today-open").querySelector(".dl-from"),
     "and carries no rolled-over marker, because it did not roll");
  ok(inLane(d, "today-open") === "open" && inLane(d, "clone-card") === "done",
     "today's tasks and earlier days' share the one board");
  ok(/rolled over from an earlier day/.test(d.getElementById("board-rolled").textContent),
     `the note switches to a plain rolled count — "${d.getElementById("board-rolled").textContent}"`);
  ok(d.querySelector(`.dl-day.today[data-day="${TODAY}"]`),
     "and today's own day block is marked as today");
  ok(d.querySelectorAll(".kb-ctx:not([hidden])").length >= 2,
     `each contributing group keeps its authored prose above the lanes — ${d.querySelectorAll(".kb-ctx:not([hidden])").length} shown`);
  ok([...d.querySelectorAll(".kb-ctx:not([hidden])")].every(c => c.querySelector(".dl-why")),
     "and the prose is the paragraph, not a chip");

  console.log(`\n${P} passed, ${F} failed`);
  process.exit(F ? 1 : 0);
})();
