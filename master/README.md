# master/ — the canonical résumé source

**`master/upgrad_resume.html` does not exist yet, and nothing exports until it does.**

That is deliberate. v1's master was assembled from "bits and pieces"; v2 derives it from
`professional-journey.md`, which is the source of truth. Author it against
`upgrad_resume.template.html`, which carries the exact section contract the bot parses.

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
| `quick-skills-tls` | `<ul><li>` | "Technology Leadership & Strategy" |
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

- The **role title on the 2025–26 VoltusWave line**. v1 exported an IC-facing title on
  IC requisitions while the employment title was VP of Technology. On an IC-only track
  this needs one accurate answer, not a per-requisition switch. The 2017 **Co-Founder
  and VP** role is historical and unambiguous.
- The **total years figure**. v1 held it in two places in one file and they silently
  disagreed. Keep it in one place, or grep after every change.
- Any metric that reads as a measured result but came from a burst test.
