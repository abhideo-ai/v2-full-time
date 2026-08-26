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

// Section 10 writes a synthetic day into daily/days.json — his source of truth,
// not a fixture. run.sh puts it back, but the header of this file says it can be
// run on its own, and on its own it left the synthetic day behind permanently.
const DAYS_PATH = REPO + "/daily/days.json";
const DAYS_BACKUP = fs.readFileSync(DAYS_PATH, "utf8");
process.on("exit", () => {
  if (fs.readFileSync(DAYS_PATH, "utf8") === DAYS_BACKUP) return;
  fs.writeFileSync(DAYS_PATH, DAYS_BACKUP);
  try { regenerate(); } catch { /* the page is stale, the source of truth is not */ }
});

// A canned HTTP failure, for the sections that have to see a write REFUSED. The
// server is real and healthy, and a real 503 cannot be produced on demand
// without taking the database away from every other section in the file.
const fail = (status, error) => Promise.resolve(new Response(JSON.stringify({ error }),
  { status, headers: { "Content-Type": "application/json" } }));

async function boot(base, seed, wrap) {
  const html = fs.readFileSync(REPO + "/daily/index.html", "utf8");
  const js = fs.readFileSync(REPO + "/static/todo.js", "utf8");
  const dom = new JSDOM(html, { url: base + "/daily/", runScripts: "outside-only" });
  const w = dom.window;
  // Seeding localStorage BEFORE the script boots is the only way to hand the
  // page a state row whose done_at / moved_at is not today — which is exactly
  // the case the board's membership rules turn on, and the case a live run can
  // never manufacture through the API.
  if (seed) w.localStorage.setItem("v2-daily-todo", JSON.stringify(seed));
  // jsdom has no fetch; hand it Node's, resolving relative paths at `base`.
  const net = (u, o) => fetch(u.startsWith("http") ? u : base + u, o);
  w.fetch = wrap ? wrap(net) : net;
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
  // "Where things stand" carries the ready-and-unsent backlog gate — the one
  // number on this page that decides anything. It was scraped out of the root
  // launcher's #app-list, which has been empty markup since the launcher started
  // rendering from /api/jobs, so it read a confident `0 built · 0 sent ·
  // backlog 0` over a database holding four live seats.
  const jobs = await (await fetch(API + "/api/jobs")).json();
  const standing = d.getElementById("standing").textContent;
  ok(new RegExp(`\\b${jobs.counts.total}\\b job workspaces built`).test(standing),
     `the built count comes from the database — ${jobs.counts.total} row(s), page says "${standing.match(/\d+ job workspaces built/)}"`);
  ok(new RegExp(`backlog\\s+${jobs.counts.ready}\\b`).test(standing),
     `and so does the backlog gate — /api/jobs says ready ${jobs.counts.ready}`);
  ok(!/backlog\s+0,/.test(standing) || jobs.counts.ready === 0,
     "a zero backlog is only ever reported when the database really holds none");

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

  console.log("\n1c. A lane you cannot drop onto is not a lane");
  // Comments stripped first — the comment explaining why the `:empty` rule was
  // removed quotes the rule, and matched the assertion that it is gone.
  const css = fs.readFileSync(REPO + "/style.css", "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  ok(/\.kb-drop\s*\{[^}]*min-height:\s*3\d/.test(css), "a drop zone reserves a body");
  ok(!/\.kb-drop:empty\s*\{[^}]*min-height:\s*0/.test(css),
     "and does NOT give that up when empty — `.dl-list` has no padding, so an " +
     "empty lane rendered 0px tall and could not be dropped onto at all");
  ok([...d.querySelectorAll(".kb-drop")].every(z => z.getAttribute("aria-label")),
     "every zone names itself for a screen reader");
  ok(d.getElementById("move-hint").getAttribute("role") === "alert",
     "the reason-gate refusal is an alert — the one rule this page enforces must be SPOKEN, not just shown");
  // The default `align-items: stretch` on a wrapping row is what shipped
  // stretched oval pills on the workspace index pages an hour before this board.
  // `.kb-context` wants stretch — they are cards on a row and should share a
  // height — but stretch by DEFAULT and stretch by CHOICE read the same in a
  // browser and differently to whoever edits the rule next.
  for (const sel of ["\\.dl-actions", "\\.dl-dialog-actions", "\\.dl-meta", "\\.dl-reason",
                     "\\.kb-context"]) {
    const rule = new RegExp(`^${sel}\\s*\\{([^}]*)\\}`, "m").exec(css);
    ok(rule && /align-items:/.test(rule[1]), `${sel.replace(/\\/g, "")} pins its cross-axis`);
  }

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
  // A REVIVABLE reason, deliberately: this section is the round trip, and
  // "Already applied, or duplicates another" is terminal, so restoring it is now
  // refused on purpose. Section 5g is where that refusal is asserted.
  await move(w, "paste-11-15", "dropped", ["jd-changed"], "");
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
  // role="alert" announces a CHANGE. The refusal used to only un-hide an element
  // that was already visible, so the second reasonless confirm — the one you
  // make when you did not hear the first — mutated nothing and said nothing.
  let hintChanges = 0;
  const hintObs = new w.MutationObserver(() => hintChanges++);
  hintObs.observe(d.getElementById("move-hint"),
                  { childList: true, characterData: true, subtree: true, attributes: true });
  await confirmMove(w);
  hintObs.disconnect();
  ok(hintChanges > 0,
     `a SECOND reasonless confirm changes the alert too, so it is spoken again — ${hintChanges} mutation(s)`);
  ok(inLane(d, "fix-el-paso") === "open", "and it still has not moved");
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

  console.log("\n5e. The keyboard path does not dead-end");
  // A lane move re-parents the <li>, and re-parenting blurs what was focused
  // inside it — so the handle you just pressed a key on lost focus, and the
  // next arrow key went to <body>. One move was all a keyboard user got.
  let grab = li(d, "journey-doc").querySelector(".kb-grab");
  grab.focus();
  ok(d.activeElement === grab, "the handle takes focus");
  await arrow(w, "journey-doc", "ArrowRight");
  ok(inLane(d, "journey-doc") === "done", "one arrow moves the card");
  ok(d.activeElement === li(d, "journey-doc").querySelector(".kb-grab"),
     "and focus is STILL on the handle, so the next key works too");
  await arrow(w, "journey-doc", "ArrowLeft");
  ok(inLane(d, "journey-doc") === "open", "the second key really does work");
  await arrow(w, "journey-doc", "ArrowLeft");
  ok(inLane(d, "journey-doc") === "open", "there is nothing left of Open");
  ok(/No lane before open/.test(d.getElementById("kb-say").textContent),
     `and the dead end is announced rather than silent — "${d.getElementById("kb-say").textContent}"`);
  ok(!d.getElementById("kb-say").hidden, "the live region is visible when it speaks");
  // The handle is also how you FOCUS a card for those arrow keys, and clicking
  // it is how you focus it with a mouse. `draggable` is deferred to a pointer
  // hold precisely so the detail text — the instruction on most of these tasks —
  // stays selectable; only `dragend` cleared it, and dragend never fires when no
  // drag started, so one click armed the card for the rest of the session.
  const held = li(d, "journey-doc");
  grab = held.querySelector(".kb-grab");
  grab.dispatchEvent(new w.Event("pointerdown", { bubbles: true }));
  ok(held.draggable === true, "holding the handle arms the drag");
  grab.dispatchEvent(new w.Event("pointerup", { bubbles: true }));
  ok(held.draggable === false,
     "and letting go WITHOUT dragging disarms it — otherwise a click on the handle makes the card's text unselectable for good");

  console.log("\n5f. Enter inside the dialog confirms; it does not reload the page");
  // The form holds exactly one implicit-submission-blocking field (the date) and
  // no submit button, so Enter submitted it: a GET to the current URL, i.e. a
  // reload with the move discarded.
  await openMove(w, "verify-pdf", "pushed");
  const form = d.querySelector("#move-dialog form");
  let submit = new w.Event("submit", { bubbles: true, cancelable: true });
  form.dispatchEvent(submit);
  await settle();
  ok(submit.defaultPrevented, "the submit is cancelled — no navigation");
  ok(!d.getElementById("move-hint").hidden, "and Enter with no reason hits the SAME gate");
  ok(inLane(d, "verify-pdf") === "open", "the card did not move");
  ok(!(await dbState())["2026-08-25::verify-pdf"], "and nothing was written");
  const until = d.getElementById("move-until");
  const tomorrow = iso(new Date(now.getTime() + 86400000));
  ok(until.min === tomorrow,
     `a push cannot be dated today — laneOf() returns an arrived push to Open, so that writes an already-expired move (min ${until.min})`);
  d.querySelector('#move-reasons input[value="blocked"]').checked = true;
  submit = new w.Event("submit", { bubbles: true, cancelable: true });
  form.dispatchEvent(submit);
  await settle();
  ok(inLane(d, "verify-pdf") === "pushed", "Enter with a reason completes the move");
  li(d, "verify-pdf").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();

  console.log("\n5g. 'Closed for good' is a rule, not a caption");
  // paste-jds was parked in section 3 with TWO terminal reasons, and the card
  // has said "closed for good" ever since — next to a Restore button that
  // restored it anyway. `./todo backlog` already withheld its restore hint from
  // exactly these tasks, so the tool believed the rule and did not enforce it.
  const pj = li(d, "paste-jds"), pjRestore = pj.querySelector('.dl-act[data-act="restored"]');
  ok(pj.querySelector(".dl-revivable").textContent === "closed for good", "the card says so");
  ok(!pjRestore.hidden,
     "Restore stays VISIBLE — a refusal you cannot reach is a refusal you cannot be told about");
  pjRestore.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  ok(inLane(d, "paste-jds") === "parked", "and clicking it does NOT bring the task back");
  ok((await dbState())["2026-08-25::paste-jds"].moved === "parked", "nothing was written");
  const refusal = d.getElementById("kb-say").textContent;
  ok(/Posting no longer active/.test(refusal), `the refusal names the reason that closed it — "${refusal}"`);
  ok(/reason that can come back/.test(refusal),
     "and the way back, so it is a refusal rather than a dead end");
  // The other half: a park whose reasons can ALL come back is untouched by this.
  await move(w, "paste-1-10", "parked", ["blocked"], "");
  li(d, "paste-1-10").querySelector('.dl-act[data-act="restored"]')
    .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();
  ok(inLane(d, "paste-1-10") === "open", "a revivable park still restores normally");

  console.log("\n5h. A card lands in the lane you aimed at, not a neighbouring one");
  // `restored` clears the move but deliberately NOT the tick, so a card ticked
  // and THEN parked came back to Done — while the live region said "Restored."
  await tick(w, "paste-1-10");
  await move(w, "paste-1-10", "parked", ["blocked"], "");
  ok(inLane(d, "paste-1-10") === "parked", "tick then park lands in Parked — `moved` outranks `done`");
  ok((await dbState())["2026-08-25::paste-1-10"].done === true, "and the tick is still on record");
  await drag(w, "paste-1-10", "open");
  ok(inLane(d, "paste-1-10") === "open",
     `dropped on Open it lands in OPEN, not Done — got ${inLane(d, "paste-1-10")}`);
  ok(/Restored/.test(d.getElementById("kb-say").textContent),
     `and is announced as the restore it was — "${d.getElementById("kb-say").textContent}"`);
  const p110 = (await dbState())["2026-08-25::paste-1-10"];
  ok(!p110.moved && p110.done === false,
     "both ops landed in one request, so the row and the lane agree");
  ok(!li(d, "paste-1-10").querySelector("input").checked, "and the checkbox agrees too");

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
  // Offline there is no db.validate and no CHECK constraint, so the reason rule
  // has to hold here on its own. It does not get a pass for being the easy mode.
  await openMove(w, "fix-el-paso", "dropped");
  await confirmMove(w);
  ok(!d.getElementById("move-hint").hidden, "a reasonless drop is refused offline too");
  ok(inLane(d, "fix-el-paso") === "open", "the card stays put");
  ok(!JSON.parse(w.localStorage.getItem("v2-daily-todo"))["2026-08-25::fix-el-paso"],
     "and NOTHING reaches localStorage — the store with no database behind it");
  d.getElementById("move-cancel").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await settle();

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
  const doc = JSON.parse(fs.readFileSync(DAYS_PATH, "utf8"));
  doc.days.push({ date: TODAY, groups: [{ title: "Authored for today", kind: "parallel",
    why: "synthetic test day", items: [
      { id: "today-open", p: 1, needs: [], task: "Due today", detail: "" },
      { id: "today-blocked", p: 2, needs: ["today-open"], task: "Blocked today", detail: "" }] }] });
  fs.writeFileSync(DAYS_PATH, JSON.stringify(doc, null, 2) + "\n");
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

  console.log("\n11. Membership is recomputed, not decided once at boot");
  if (fs.readFileSync(REPO + "/daily/index.html", "utf8").includes('data-day="2026-08-24"')) {
    const YESTERDAY = iso(new Date(now.getTime() - 86400000));
    // Two rows a live run cannot produce: both were acted on BEFORE today.
    w = await boot(PLAIN, {
      // Pushed days ago, and its return date is today.
      "2026-08-24::old-open": { done: false, moved: "pushed", until: TODAY,
                                reasons: ["blocked"], moved_at: `${YESTERDAY}T20:00:00` },
      // Finished before today, so it is off the board and back in its day list.
      "2026-08-24::old-done": { done: true, done_at: `${YESTERDAY}T10:00:00` },
    });
    d = w.document;
    ok(inLane(d, "old-open") === "open",
       `a push whose return date has ARRIVED is back on the board — got ${inLane(d, "old-open")}. ` +
       "Membership tested `!moved`, so laneOf sent it to Open and it was never put on the board to be placed there");
    ok(li(d, "old-open").querySelector(".dl-due").textContent === "due today",
       "due against its return date");
    ok(!li(d, "old-open").classList.contains("moved"),
       "and it is not styled as moved out — it is back in play");
    ok([...li(d, "old-open").querySelectorAll(".dl-act:not([hidden])")]
       .map(b => b.dataset.act).includes("pushed"),
       "its Park/Push/Drop buttons agree with the lane it is sitting in");

    ok(!d.querySelector('.kb-drop > li[data-id="old-done"]'),
       "a task finished on an EARLIER day is not on today's board");
    ok(d.querySelector('.dl-day[data-day="2026-08-24"] li[data-id="old-done"]'),
       "it is back in its own day's list");
    // The trapdoor: parking from the day list wrote `moved` to the store and
    // left the card exactly where it was, with the Parked zone still reading 0.
    await move(w, "old-done", "parked", ["blocked"], "");
    ok(inLane(d, "old-done") === "parked",
       `acting on an off-board card puts it ON the board — got ${inLane(d, "old-done")}`);
    ok(d.getElementById("moved-parked").querySelector(".n").textContent === "1",
       "and the Parked count sees it, instead of showing 0 over a real park");
    ok(!d.querySelector('.dl-day[data-day="2026-08-24"] li[data-id="old-done"]'),
       "one node, one place — it left the day list rather than being cloned");
    li(d, "old-done").querySelector('.dl-act[data-act="restored"]')
      .dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    await settle();
    ok(d.querySelector('.dl-day[data-day="2026-08-24"] li[data-id="old-done"]'),
       "and restoring a done card sends it home again — the board is not a one-way trapdoor");
  } else {
    console.log("  SKIP  (single-day log — caller did not add the synthetic day)");
  }

  console.log("\n12. A REFUSED write changes nothing on screen");
  // The board's own rule, turned on the failure path. A checkbox is the trap:
  // the browser flips it before the handler runs, and act() only re-rendered on
  // success — so a refused tick sat ticked over a database holding nothing,
  // while the live region cheerfully said the move had happened.
  let refusing = true;
  w = await boot(API, null, net => (u, o) =>
    refusing && String(u).includes("/api/ops")
      ? fail(503, "database unreachable: forced by the test")
      : net(u, o));
  d = w.document;
  const key12 = `${TODAY}::today-open`;
  const box12 = li(d, "today-open").querySelector("input");
  box12.checked = true; box12.dispatchEvent(new w.Event("change"));
  await settle(200);
  ok(box12.checked === false, "a refused tick does not stay ticked");
  ok(inLane(d, "today-open") === "open", "and the card does not change lane");
  ok(!(await dbState())[key12], "the database holds nothing, which is what the board now shows");
  ok(d.getElementById("store-banner").className.includes("bad"), "the banner turns red");
  ok(/Not saved/.test(d.getElementById("store-banner").textContent), "and says it was not saved");

  await move(w, "today-open", "parked", ["blocked"], "");
  ok(inLane(d, "today-open") === "open", "a refused park leaves the card exactly where it was");
  ok(!(await dbState())[key12], "still nothing in the database");
  ok(d.getElementById("kb-say").textContent === "",
     `and the live region claims NOTHING — it is the only channel a screen reader has (said "${d.getElementById("kb-say").textContent}")`);

  refusing = false;
  box12.checked = true; box12.dispatchEvent(new w.Event("change"));
  await settle(200);
  ok((await dbState())[key12]?.done === true, "the next write lands");
  ok(inLane(d, "today-open") === "done", "and the card follows it");
  ok(d.getElementById("store-banner").className.includes("ok"),
     "and the banner goes back to naming the store — a red banner that outlives its failure sits over writes that are working");

  // The probe answers, the read does not: the database went away between the two
  // calls. Rendering localStorage under "Saving to PostgreSQL" is the same defect
  // as any other board state the database does not hold.
  w = await boot(API, { "2026-08-25::clone-card": { done: true, done_at: `${TODAY}T08:00:00` } },
    net => (u, o) => String(u).includes("/api/state") ? fail(503, "gone") : net(u, o));
  d = w.document;
  ok(d.getElementById("store-banner").className.includes("warn"),
     "a probe that succeeds over a read that fails demotes to local and SAYS so");
  ok(d.getElementById("store-banner").textContent.includes("serve.py"),
     "with the same instructions the plain-server path gives");

  console.log(`\n${P} passed, ${F} failed`);
  process.exit(F ? 1 : 0);
})();
