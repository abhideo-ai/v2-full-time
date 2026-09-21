# RETIRED — the upGrad / Hiration pipeline

**⛔ THIS DESCRIBES A PIPELINE THAT NO LONGER EXISTS. It is history, not instruction.**
His upGrad access was revoked on 2026-08-27. Every entry point refuses with exit 3
(`automation/upgrad_retired.py`). Do not try to revive it and do not diagnose the refusal
as a bug. Lifted out of CLAUDE.md on 2026-09-21 to cut the rulebook injected into every
subagent; nothing here governs current behaviour.

**The two things from this block that ARE still operative live in CLAUDE.md, not here** —
see *Layout & automation*: `upgrad_resume_paste.py` is the shared résumé parser and is
load-bearing for the current path, and `cleanup_cards.py` is still never run.

---

> ## ⛔ RETIRED 2026-08-27 — the seven sections below describe a pipeline that NO LONGER EXISTS
>
> **⛔ HIS UPGRAD ACCESS WAS REVOKED on 2026-08-27.** His words: *"My access to upgrad has been
> revoked."* The résumé builder, both Hiration cards and every stored credential are unreachable.
> This is not a preference any more; nothing in these sections can be run, and every entry point
> now refuses with exit 3 (`automation/upgrad_retired.py`). **Do not try to revive it, and do not
> diagnose the refusal as a bug.**
>
> **⚠ `master/live_card_dump*.json` and `.md` are now the ONLY surviving record of what those two
> cards contained.** They cannot be refreshed. They are committed; keep them.
>
> **⚠ `master/Abhisheik_Deo_Resume.pdf` is the LAST upGrad export (25 Aug) and it is now WRONG.**
> It says **Knockout.js** and **300**, and predates AngularJS, 280, Kubernetes, Terraform and the
> axe DevTools bullets. **It must never be sent.** The next real PDF comes out of Canva.
>
> **⛔ `automation/upgrad_resume_paste.py` IS NOT PART OF THIS.** Despite the name it is the shared
> résumé PARSER, imported by `resume_db.py`, `jobs_sync.py`, `daily.py`, `resume.py` and
> `workspace_favicon.py`. It is load-bearing for the CURRENT path and is deliberately NOT guarded.
>
> **Set by him: we are moving off the upGrad / Hiration résumé builder. Résumé layout and PDF
> export are done by hand in Canva Pro from now on, and the upGrad login/export step has been
> removed from the automation workflow.**
>
> Everything from here to *Naukri quirk* — **upGrad export · Which master card · Card deletion ·
> Copy blocks · Pasting into Hiration · Editing the card itself · upGrad paste quirk** — is kept
> as history, not as instruction. Do not run it, do not re-add it to `daily/days.json`, and do not
> plan work around it.
>
> **The files stay. He said so explicitly: "do not remove the files. just remove the step from the
> automation workflow."** All nine scripts remain on disk — `upgrad_apply.py`, `upgrad_login.py`,
> `upgrad_creds.py`, `upgrad_resume_paste.py`, `browser.py`, `cleanup_cards.py`,
> `fix_master_card.py`, `dump_card.py`, `update_master_card.py` — along with both Hiration cards
> and the encrypted credentials. Legacy, not garbage. **`cleanup_cards.py` is still never run.**
>
> **What changes in practice:**
> - `master/upgrad_resume.html` is now the **complete content source**, not a ten-section paste
>   feed. It already carries everything the card used to own: the dates table for all ten roles,
>   Education, Certifications, and Personal Information (Hyderabad · +91 93640 27487 ·
>   abhisheik@abhideo.ai · LinkedIn `abhisheikdeo`). Nothing is trapped in Hiration.
> - The **paste matrix is moot.** `<p>`-versus-`<ul>` and the synthetic `ClipboardEvent` existed
>   solely to force bold and bullets through Draft.js. Canva has no such constraint.
> - There is **no ATS "Resume Review" score** any more. CLAUDE.md already said not to chase it.
> - **`verify-pdf` is now the only gate.** Nothing upstream enforces dates, bold, the LinkedIn slug
>   or the 3-page cap — a hand-built PDF can drift in ways no script catches.
>
> **Two ATS risks specific to Canva, worth stating once:** most Canva résumé templates are
> two-column with icons, and a multi-column PDF is the classic parsing failure — the reader
> interleaves bullets across columns. Single column, real text boxes, nothing baked into shapes.
> And `resume-issues-to-avoid/` rule 9 is exactly the bold-stripped-on-export failure; verify bold
> on the exported file, not in the editor.
>
> Still open, his call: whether the per-workspace `bullets_for_upgrad.html` artefact and the
> `upgrad_resume.html` filename should be renamed now that nothing pastes into upGrad.


### upGrad export

```
UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py \
    --slug <slug> --no-pause --reset
```

Run from the repo root. It clones a master Hiration card, overwrites **the ten parsed
sections** — headline, summary, three skills blocks, five experience roles — from the
workspace's `upgrad_resume.html`, exports `<workspace>/Abhisheik_Deo_Resume.pdf`, and
prints ATS JSON. The persistent browser profile (`.playwright-profile/`) sits at the repo
root, so **cwd matters**. Login is automated from encrypted credentials in `automation/`
— gitignored, **never commit them**. The bot runs serially (shared browser).

### Which master card

Two live masters, both in `cleanup_cards.py`'s `PROTECTED` set:

- **`august_ic_master_resume`** — the IC card. **Created by cloning `august_master_resume`,
  not from blank.** That base already carries all ten experience entries — the five the bot
  writes plus the five pre-2016 roles it never touches — along with dates, education and
  certifications. So building the IC card is **overwriting text in an existing skeleton**, not
  creating sections. Content comes from `master/upgrad_resume.html`. It is the **script
  default** as of 2026-08-25 — a bare export uses it, no flag needed.
  **The name is not finalised.** Until a card exists in Hiration under exactly this name,
  every export fails loudly at `stage_find_master` with a "check the card name, or pass
  `--master`" message. That loud failure is intended; the previous silent fallback to the
  other card was the bug. Renaming means one line in `upgrad_apply.py`, one in
  `cleanup_cards.py`'s `PROTECTED`, and this block.
- **`august_master_resume`** — kept deliberately; it may still be used for future positions,
  and it is the base the IC card is cloned from. No longer the default: reach it explicitly
  with `--master august_master_resume`.

### ⛔ Card deletion — ask first, every time

**Never run `cleanup_cards.py` at all until he explicitly says to delete a specific card.**
Not after an export, not after a submission, not as tidy-up. He asks, by name, or it does not
run. A bare, slug-less run deletes every temp card; even `--slug <slug>` is his call to make,
not a follow-up to infer. Tailored `<slug>_ats_resume` cards accumulating is the intended
state, not a mess to clean.

**⚠ Dates live in the Hiration card, not the HTML.** The bot overwrites bullet text only, so
the card itself must already read Apr 2026. On `august_master_resume` it already does
(VoltusWave 2025-03-01 → 2026-04-01, Deque 2019-12-01 → 2025-02-01) — **verify after cloning
rather than assuming a clone preserved them.**

**Education, certifications and the pre-2016 roles are card-only** — the bot never touches
them. They already exist on the card, carried over from v1, so the work is correcting their
text by hand in the Hiration UI. **The one that matters is El Paso**: it is a Java role —
Senior Java Developer, JSP and Java Enterprise Edition, Tennessee Gas Pipeline — and the v1
card describes it as .NET, hiding four of the eleven Java years.

**Verify every exported PDF:** dates correct (VoltusWave ended **Apr 2026**), bold renders
heavier, content matches `bullets_for_upgrad.html`, contact details and the LinkedIn slug
**`abhisheikdeo`** (not `abhideo` — that is the email domain), no `[fill in metric]`, and
**≤3 pages**. The ATS "Resume Review" score wobbles 87–99 on hygiene, not JD
fit — don't chase it. (No print dialog is involved: the bot exports headlessly and
`html_to_pdf.py` uses Playwright's own PDF call. If a résumé PDF ever comes from a source
document instead, export it from that application rather than via the browser's Print to PDF,
which flattens bold.)

`automation/html_to_pdf.py` renders any workspace HTML to PDF via headless Chromium.

### Copy blocks — one whole section, always

**A copy block is one complete section that REPLACES its counterpart wholesale. Never a fragment
to merge into an existing block.** Set 2026-08-25, and it holds for the master résumé and for
every per-job résumé.

- One button, one section, one paste. He selects the section in Hiration, deletes it, pastes.
- **Never** "add this line to Engineering Excellence" or "paste these two bullets under the third
  one". A partial paste means reading the existing block, working out where the new text goes, and
  not duplicating what is already there — three chances to get it wrong, silently, in a field he
  cannot easily diff afterwards.
- If a section changed by one word, the block still carries the **whole** section.
- **Key Skills is one section, not three.** It renders as three sub-groups —
  Technology Leadership & Strategy, Engineering Excellence, Business & Delivery — but when
  tailoring per job it is **replaced whole**, all three groups at once. The paste sheet carries a
  combined block for exactly this. Set by him 2026-08-25.
- **His skills format is short capability labels, not sentences** — `Multi-Tenant SaaS
  Architecture (Shared-Schema, Per-Tenant Isolation, Regulated Carve-Outs)`, never a descriptive
  clause. It scans; prose does not. Match it.
- **Generate copy blocks FROM the résumé file, never retype them.** A paste sheet that disagrees
  with the file the bot writes from is the drift that merging three files into one removed.
- Content that did not make it into a section is **not offered for pasting at all** — record it as
  considered-and-not-applied, with no copy affordance, so nothing loose invites a hand-paste.
- `data-copy-html="1"` on every button. A hand-dragged selection loses bold, and that does not
  surface until the exported PDF.

### Pasting into Hiration — the matrix, settled 2026-08-25

**No markup gives both bold and bullets through a real clipboard paste.** Tested by him, all
three cases:

| shape | bold | bullets |
|---|---|---|
| `<p>` per line, pasted alone | ✅ | ❌ |
| several `<p>` at once | ✅ | ❌ collapses to one line |
| `<ul><li>` compact | ❌ | ✅ |

His console output proved the clipboard itself is correct — 18 `<strong>` tags, `ClipboardItem`
present, rich path taken. **Hiration strips it on the way in.** Whitespace between tags was ruled
out too. Do not go looking for a fourth markup shape; the space is mapped.

**THE EXPORTER IS THE PATH.** `_paste_html` in `upgrad_apply.py` dispatches a *synthetic*
`ClipboardEvent` carrying `text/html` straight into Draft.js, which honours `<ul>`, `<li>` and
`<strong>` natively. That is where v1's "100% formatting carried over" actually came from — the
bot, never hand-pasting. A page on `localhost` cannot do this to an iframe on `upgrad.com`;
only Playwright can.

**So the ten parsed sections never need pasting by hand.** The exporter overwrites every one of
them from `<workspace>/upgrad_resume.html` on each run. The paste sheet is for *reading* what the
bot will write, and for one-off single-line fixes where `<p>` alone works.

**⚠ The upGrad onboarding modal blocks everything.** "Let's kickstart your career journey" renders
in the **top-level page** and overlays the iframe, so every click fails with *"subtree intercepts
pointer events"*. `_dismiss_modals` sweeps **every frame** — clearing only the app frame finds
zero, which is the trap. `stage_nav` retries the click once after clearing.

### Editing the card itself

`automation/fix_master_card.py` edits the **card-only** material the exporter never touches — the
five pre-2016 roles. Title and company are contenteditable divs with stable ids
(`PR_designation_N`, `PR_company_N`); bullets are a Draft.js editor inside `#PR-child-N`. It
refuses to touch a role whose current title is not what it expects, so it cannot silently rewrite
the wrong entry.

**Known limit:** bullet rewrites on the pre-2016 roles show in the editor and then **do not
survive the save**. The title does. Those three El Paso bullets are his to paste by hand.

### upGrad paste quirk

upGrad keeps raw `<strong>` but **strips styled `<span>`s, and strips bold from
list-rooted content**. So `bullets_for_upgrad.html` restates each changed bullet as a
standalone `<p>` with raw `<strong>` — never inside a `<ul>`.

