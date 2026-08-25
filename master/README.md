# master/ — the canonical résumé source

**`master/upgrad_resume.html` is the single master résumé.**

One file, two readers: he pastes sections 1–15 into the Hiration card by hand, and
`automation/upgrad_resume_paste.py` parses ten of them by id for the bot. It replaced a three-file
split on 2026-08-25 — a parsed copy, a hand-paste copy and a blank template — whose sections 1–10
were duplicated verbatim and could drift apart without anyone noticing.

Every bullet is a standalone `<p>`, never inside a `<ul>`: upGrad's paste sanitiser strips bold from
list-rooted content. `_ul_items_html` reads **both** shapes, so the same file serves both readers.

---

## The parser contract

`automation/upgrad_resume_paste.py` reads **ten** sections. Each is:

```html
<div class="section copy-target" id="quick-<name>">
  <button class="copy-btn" data-copy-target="#quick-<name>">Copy</button>
  <!-- a <p> for prose, or a <ul><li> for bullets -->
</div>
```

| id | shape | parsed as |
|---|---|---|
| `quick-headline` | `<p>` | plain text |
| `quick-summary` | `<p>` | HTML, `<strong>` preserved |
| `quick-skills-tls` | `<p>` or `<ul><li>` | "Technology Leadership & Strategy" |
| `quick-skills-ee` | `<ul><li>` | "Engineering Excellence" |
| `quick-skills-bd` | `<ul><li>` | "Business & Delivery" |
| `quick-vp` | `<ul><li>` | experience 0 |
| `quick-deque` | `<ul><li>` | experience 1 |
| `quick-rocket` | `<ul><li>` | experience 2 |
| `quick-voltuswave-cofounder` | `<ul><li>` | experience 3 |
| `quick-teletext` | `<ul><li>` | experience 4 |

**Traps, all of them silent:**

- A **missing or misspelled id is skipped without error** — that section simply never
  reaches upGrad, and the export looks successful. Diff the PDF against the source.
- **Experience order is fixed** (`EXPERIENCE_KEYS`) and maps to the editor's
  `PR-child-0..4`. Reordering the divs reorders nothing; renaming an id drops the role.
- **Dates are not in this file.** They live in the Hiration card. The VoltusWave role
  ended **Apr 2026** and the card must say so.
- `upgrad_apply.py` refuses to run on an empty/placeholder file — it calls this the
  "14-section contract" in its error text, which is stale wording. There are ten.
- `**/upgrad_resume.html` is gitignored **except** this one. Per-job copies are derived
  and disposable; this file is the only one that must survive.

## What still has to be settled before the first export

Carried over from v1 as open, not as fact — resolve each against
`professional-journey.md` rather than against the old résumé:

- The **role title on the 2025–26 VoltusWave line**. His employment title was VP of
  Technology; v1 resolved this by having the single master card (`august_master_resume`)
  render **"Principal Software Architect"** for every seat, leadership included — verified
  2026-08-18. On an IC-only track that convention is the one to carry, but it is his call to
  confirm, not an assumption to inherit. The 2017 **Co-Founder and VP** role is historical
  and unambiguous — it stays as-is.
- The **total years figure**. v1 held it in two places in one file and they silently
  disagreed. Keep it in one place, or grep after every change.
- Any metric that reads as a measured result but came from a burst test.
