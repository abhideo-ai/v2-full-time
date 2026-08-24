// Copy-to-clipboard for buttons with data-copy-target="<css selector>".
// Opt-in rich-text: add data-copy-html="1" to also write text/html so
// bold/italics paste through into Google Docs / Word / Notion.
// When the .copy-btn lives INSIDE the target (the common .section.copy-target
// pattern), the button's own text is stripped from the copied content via a
// cloned-and-cleaned subtree so it never lands in the clipboard.
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".copy-btn");
  if (!btn) return;
  // Two supported markups: (1) explicit data-copy-target="<css selector>" on
  // the button, or (2) the documented .paste-area.copy-target pattern where
  // the button lives INSIDE the copy block and carries no selector — fall
  // back to the nearest ancestor .copy-target. The .copy-btn is stripped from
  // the clone below, so copying the enclosing container is safe.
  const target = btn.dataset.copyTarget
    ? document.querySelector(btn.dataset.copyTarget)
    : btn.closest(".copy-target");
  if (!target) return;
  const clone = target.cloneNode(true);
  clone.querySelectorAll(".copy-btn, [data-copy-skip]").forEach(n => n.remove());
  // Snapshot HTML before mutating clone for plain-text extraction. Three
  // transforms applied for paste-sanitizer compatibility:
  // (1) Wrap in <div> so the HTML root is never a list element. Some paste
  //     sanitizers treat <ul>/<ol>-at-root as "raw list block, replace
  //     mine" and strip inline formatting; <div> at root keeps them in
  //     "rich text" mode.
  // (2) Replace <strong>...</strong> with <span style="font-weight:700">
  //     ...</span>. Some restricted-schema rich-text editors (notably the
  //     upGrad resume builder) disallow semantic bold tags inside <li>
  //     entirely but permit <span> with arbitrary inline styles. <span>
  //     with font-weight is the universal fallback for "bold survives
  //     anywhere".
  // Google Docs, Word, Notion, LinkedIn (plain-text path) all unaffected.
  // Keep raw <strong>: upGrad's paste sanitizer PRESERVES <strong> but STRIPS
  // styled <span>s, so the previous <strong>→<span style="font-weight:700">
  // transform was itself the cause of bold loss on paste into upGrad. v2's
  // known-good path is a manual browser copy that keeps <strong> untouched.
  // Google Docs / Word / Notion / LinkedIn all honor <strong> fine too.
  const html = `<div>${clone.innerHTML.trim()}</div>`;
  // LinkedIn (and any plain-text target) strips HTML on paste, so the
  // text/plain alternate is what actually lands there. Inject "• " before
  // each <li> and a newline after, plus a blank line after each <p>, so
  // bullets and paragraph breaks survive — without this, <ul><li>a</li>
  // <li>b</li></ul> collapses to "ab" with no structure.
  clone.querySelectorAll("li").forEach(li => {
    li.insertBefore(document.createTextNode("• "), li.firstChild);
    li.appendChild(document.createTextNode("\n"));
  });
  clone.querySelectorAll("p").forEach(p => {
    p.appendChild(document.createTextNode("\n\n"));
  });
  const text = (clone.textContent || "")
    .replace(/\n[ \t]+/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  const useRich = btn.dataset.copyHtml === "1" && window.ClipboardItem && navigator.clipboard.write;
  try {
    if (useRich) {
      await navigator.clipboard.write([new ClipboardItem({
        "text/html":  new Blob([html], { type: "text/html"  }),
        "text/plain": new Blob([text], { type: "text/plain" }),
      })]);
    } else {
      await navigator.clipboard.writeText(text);
    }
    // Persistent "Copied" state: stays marked so you can track which blocks
    // you've pasted while working top-to-bottom. Re-clicking re-copies and
    // keeps it marked. .copied class drives the green in style.css; the
    // data-copied attribute keeps the older inline-CSS pages (ANSR) working.
    btn.classList.add("copied");
    btn.dataset.copied = "1";
    btn.textContent = "Copied";
  } catch (err) {
    console.error("clipboard write failed:", err);
    btn.textContent = "Copy failed";
  }
});

// Filter bar on the dashboard — scoped to the active tab's table.
const filter = document.getElementById("filter");
if (filter) {
  filter.addEventListener("input", () => {
    const q = filter.value.trim().toLowerCase();
    document.querySelectorAll(".app-row").forEach((row) => {
      const hay = row.dataset.search || "";
      row.style.display = !q || hay.includes(q) ? "" : "none";
    });
  });
}

// Tab switcher on the dashboard. Buttons with [data-tab] toggle the
// matching [.tab-panel[data-tab="<name>"]] panel.
document.querySelectorAll(".tab-btn[data-tab]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const name = btn.dataset.tab;
    document.querySelectorAll(".tab-btn[data-tab]").forEach((b) => {
      b.setAttribute("aria-selected", b === btn ? "true" : "false");
    });
    document.querySelectorAll(".tab-panel[data-tab]").forEach((p) => {
      if (p.dataset.tab === name) p.removeAttribute("hidden");
      else p.setAttribute("hidden", "");
    });
  });
});
