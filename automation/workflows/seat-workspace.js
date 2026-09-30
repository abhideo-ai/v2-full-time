export const meta = {
  name: 'seat-workspace-3-agents-v2',
  description: 'One seat: research + tab pages and technical score + résumé proposals in parallel, then one adversarial check (3 agents, capped)',
  phases: [
    { title: 'Build', detail: 'agent 1 research + pages · agent 2 score + résumé proposals, in parallel' },
    { title: 'Check', detail: 'agent 3: one adversarial check of every claim' },
  ],
}

// His rule for this job: at most 3 agents. The guard throws rather than drifting past it.
const MAX_AGENTS = 3
let spawned = 0
function run(prompt, opts) {
  spawned += 1
  if (spawned > MAX_AGENTS) throw new Error(`agent cap reached: ${MAX_AGENTS} per job`)
  return agent(prompt, opts)
}

const A = args
// A.dir is the dated folder ("September-2026/30"), A.date the ISO date ("2026-09-30"), A.date_text the date in words.
const DIR = A.dir
const WS = `${DIR}/${A.slug}`
const SEAT = `SEAT (repo root /Users/adeo/Documents/v2-full-time):
- ${A.company}: "${A.role}", ${A.location}, ${A.mode || "on-site, full-time"}.
- Workspace: ${WS}/
- Posting: ${A.url}. He found it on LinkedIn and has NOT applied yet; this build decides whether and how to send it. Tracker status: resume_drafted.
- Inputs: ${WS}/jd.md holds the job description word for word below its marked line. job-applications/${DIR}/${A.slug}-intake.md is his paste word for word. job-applications/${DIR}/${A.slug}-image-1.png is his screenshot of the posting header (${A.screenshot}).
- Page contract: read the header comment of static/workspace.js, and start every page from its example in templates/workspace/ (delete the template comment, replace every {{…}}). ${WS}/index.html is the shared shell: never edit it. workspace.json is already written; its tabs are the template tabs plus "mismatch" (mismatch.html, his choice: the Tech mismatch table is its own tab, as in September-2026/28/nielsen-principal-member-technical-staff/mismatch.html). September-2026/28/nielsen-principal-member-technical-staff/ is the most recent finished workspace in this style; September-2026/24/tachyon-ai-architect/ is the most recent one with a tailored résumé (its proposed_edits.json and resume_changes_for_91pct_match.html).
- Ids already reserved across this workspace: research-found, files, glossary, score-line (overview); rubric, score-gates, score-unscored (score); verdict, claims, flags, gaps, sources (research); open-items, forcing-questions (questions); org-1..org-5 and copy-org-1..copy-org-5 (résumé changes). Never use a tab name as an id: overview, jd, score, resume, research, mismatch, questions${A.extra_tabs ? ", " + A.extra_tabs : ""}. Any id you add must be unique across every file in the workspace.
- automation/serve.py is running: http://127.0.0.1:8006/${WS}/index.html is the assembled page. Do not use browser automation or screenshots.
- Web search and fetch are deferred tools: load them with ToolSearch ("select:WebSearch,WebFetch"). If search runs out, curl still works. LinkedIn usually refuses fetches; the paste and the screenshot are the posting.
- Never compensation: no salary, CTC, band, equity or pay research anywhere, not even as a flag. If the JD itself mentions pay, it stays in jd.html as the JD's own words and nowhere else.`

const RESEARCH = `${SEAT}

You are agent 1 of 3 for this seat: the research and the tab pages. Agent 2 is scoring the seat and proposing résumé edits at the same time, and writes score.html, mismatch.html, score.json, proposed_edits.json and the résumé-changes page: do not create or touch those. Agent 3 will then try to refute every claim you write, so cite everything and label every inference.

Write these four files in ${WS}/:

1. jd.html: the posting from jd.md, word for word, laid out for reading with its own headings and lists as the posting has them. Nothing reworded, added or dropped (fix nothing, not even run-together words such as "Let's decode thisWe're"; keep them). Above it, the context grid: URL, received (${A.date_text}), route (LinkedIn job posting, not yet applied), and the title, location and posting facts from his screenshot.

2. research.html: cited research, folds as in the template, the verdict first and open. Cover:
${A.research}
   - Green and red flags, ranked by strength of evidence (layoffs or restructuring, what engineers say about working there, travel cadence or on-call if any source shows it), each with its sources.
   - Whether the posting is still open and when it was posted.
   - Gaps not closed, and sources (all read ${A.date_text}).

3. questions.html: two folds as in the template. First, what is still open about the seat and who can settle each. Second, forcing questions for the recruiter or hiring manager, each with why it matters. This is not interview prep.

4. overview.html: the key facts table; where it stands in two sentences (found on LinkedIn, not yet applied; a tailored résumé is being built); then EXACTLY this score line, which the main session fills in after scoring:
   <div class="callout" id="score-line"><p><strong>Technical score: pending</strong> &mdash; filled in after scoring.</p></div>
   Then three folds:
   - What the research found: the verdict and the key findings in a few sentences, linking to research.html#… anchors.
   - Files: every file in the workspace and what it is, including agent 2's score.html, mismatch.html, score.json, proposed_edits.json and resume_changes_for_<N>pct_match.html (the .docx, Abhisheik_Deo_Resume.docx, is generated by the main session afterwards); upgrad_resume.html and paste_notes.json are untouched starting files that resume.py new created, not the tailored résumé (the tailored résumé lives in the database as doc_key seat:${A.slug}); and the raw inputs in job-applications/${DIR}/.
   - Glossary: ${A.glossary} Then every acronym used on any page of this workspace. Call out collisions (for example RAG = retrieval-augmented generation vs Red/Amber/Green).

${A.extra_research || ""}

Links between your pages are plain relative links (research.html#flags, questions.html#forcing-questions); the page keeps them inside index.html. Before you finish, check that each file you wrote answers 200 at http://127.0.0.1:8006/${WS}/<file>.

Return the files you wrote, the verdict in one sentence, the strongest findings, and anything only he can confirm.`

const SCORE = `${SEAT}

You are agent 2 of 3 for this seat: the technical score and the résumé proposals. Agent 1 is researching the company and writing the other pages at the same time: do not create or touch them. Agent 3 will then try to refute every claim you write; the main session adjudicates and applies the résumé edits itself, so you PROPOSE edits, you never write to the database.

Score the job description (jd.md, below its marked line) against his record. professional-journey.md is the truth; the case studies in killer-query-case-studies/ are evidence of the work. The master résumé is in the database (jobs_tracker_v2: resume_blocks, doc_key='master', retired_at IS NULL); the seat's own copy, doc_key='seat:${A.slug}', is already cloned from it and identical. Use the résumé only to see how the record is worded today, never as evidence over the journey. September-2026/28/nielsen-principal-member-technical-staff/score.html, mismatch.html and score.json are the most recent scored seat: match their rubric style; score.json follows templates/workspace/score.json exactly (numbers only).

Scoring focus for this JD: ${A.score}
Read "e.g." and "or" generously; a named tool he has not used is a ramp item, not a zero. Where the record is disputed or open (Kubernetes: his confirmation against the interview-prep ledger; the open claims named in CLAUDE.md), say so and score only on what professional-journey.md itself shows; never resolve an open claim. Target 95+, honestly: an honest 88 beats an invented 95. Name the binding constraint and the smallest honest lift.

Write these files in ${WS}/:

1. score.html, from templates/workspace/score.html: the callout (technical score, binding constraint, smallest honest lift); the weighted rubric fold (id rubric): criterion · weight · score /10 · evidence quoted from professional-journey.md with line numbers, or a case study with file:line; the gates fold (id score-gates), named separately and not folded into the number: levelling (the JD's years bar against his years computed from the journey, and whether the title's level fits) and legitimacy (leave that to the research). The template's mismatch fold is MOVED to mismatch.html, never duplicated: in its place one sentence linking to mismatch.html, as Nielsen's score.html does.

2. mismatch.html: the "Tech mismatch & why exactly" table, like Nielsen's mismatch.html: for each JD technology or named practice he lacks or only partly has, the JD's words, what his record shows (journey line numbers), exactly why it is a mismatch (never used · used long ago · a similar tool only · not in production · never-claim), and whether it caps the score (core must-have vs ramp item).

3. score.json: numbers only, per templates/workspace/score.json. weighted_total is the score of the résumé AS PROPOSED (after your edits), scored_at "${A.date}"; the weights sum to 1.00 and the points sum to the total.

4. proposed_edits.json: an array in the shape of September-2026/24/tachyon-ai-architect/proposed_edits.json (id, section_id, ord, action, old_text, new_html, new_text, leading_verb, word_count, jd_phrases_covered, source [{file, line, quote}], risk, note). Rules: Rule 7 re-vectoring, editing ONLY the last five roles' experience bullets (section_ids quick-vp, quick-deque, quick-rocket, quick-voltuswave-cofounder, quick-teletext); edit in place and keep each bullet's leading verb unless it collides; real work only, every change traceable to a journey line; never invent a number (he has none; the safe markers are listed in CLAUDE.md); status words never upgraded. Every bullet: 25 words or fewer (count only tokens with a letter or digit), a strong verb opener never Managed/Replaced/Responsible for/Worked on/Helped, a leading verb unique across the whole document (same roots collide; the verb-pool queries are in docs/reference.md), a number or scale marker, at least one <strong> fact, no trailing period, every acronym expanded on first use in the document. old_text must match the master row's text exactly. Batch everything into this one file; fewer strong edits beat many weak ones.

5. resume_changes_for_<N>pct_match.html, from templates/workspace/resume_changes_for_Npct_match.html, N being weighted_total rounded: one section and one copy block per organisation for the five roles, in the master's order, each block holding that role's complete bullet list as it would stand after your edits (unchanged bullets included), with a short "what changed and why" line. Then set "resume_changes" in ${WS}/workspace.json to that file name (change nothing else in workspace.json).

${A.extra_score || ""}

Before you finish, check that score.json and proposed_edits.json parse and that score.html, mismatch.html and the résumé-changes page answer 200 at http://127.0.0.1:8006/${WS}/<file>.

Return the weighted total as proposed and as the master stands today, the binding constraint in one line, the smallest honest lift, the gates, the number of edits, and any evidence line you were unsure of.`

const R_SCHEMA = {
  type: 'object',
  properties: {
    files: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
    findings: { type: 'array', items: { type: 'string' } },
    confirm_with_him: { type: 'array', items: { type: 'string' } },
  },
  required: ['files', 'verdict', 'findings', 'confirm_with_him'],
}
const S_SCHEMA = {
  type: 'object',
  properties: {
    weighted_total_proposed: { type: 'number' },
    weighted_total_master: { type: 'number' },
    binding_constraint: { type: 'string' },
    smallest_honest_lift: { type: 'string' },
    gates: { type: 'string' },
    edits: { type: 'number' },
    resume_changes_file: { type: 'string' },
    unsure: { type: 'array', items: { type: 'string' } },
  },
  required: ['weighted_total_proposed', 'weighted_total_master', 'binding_constraint', 'smallest_honest_lift', 'gates', 'edits', 'resume_changes_file', 'unsure'],
}
const C_SCHEMA = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          edit_id: { type: 'string' },
          quote: { type: 'string' },
          problem: { type: 'string' },
          evidence: { type: 'string' },
          action: { type: 'string', enum: ['cut', 'fix', 'note'] },
          fix: { type: 'string' },
        },
        required: ['file', 'edit_id', 'quote', 'problem', 'evidence', 'action', 'fix'],
      },
    },
    claims_checked: { type: 'number' },
    checked_and_sound: { type: 'array', items: { type: 'string' } },
  },
  required: ['findings', 'claims_checked', 'checked_and_sound'],
}

phase('Build')
const [research, score] = await parallel([
  () => run(RESEARCH, { label: `agent 1 · research + pages (${A.short})`, phase: 'Build', schema: R_SCHEMA }),
  () => run(SCORE, { label: `agent 2 · score + résumé (${A.short})`, phase: 'Build', schema: S_SCHEMA }),
])
if (!research) log('agent 1 returned nothing; the check covers whatever files exist')
if (!score) log('agent 2 returned nothing; the check covers whatever files exist')

phase('Check')
const CHECK = `${SEAT}

You are agent 3 of 3 for this seat: one adversarial check of every claim before anything is kept. Agents 1 and 2 have written overview.html, jd.html, research.html, questions.html, score.html, mismatch.html, score.json, proposed_edits.json and a resume_changes_for_<N>pct_match.html in ${WS}/. They reported:
AGENT 1 (research and pages): ${JSON.stringify(research)}
AGENT 2 (score and résumé proposals): ${JSON.stringify(score)}

${A.extra_check || ""}

Try to refute every factual claim; when a claim is unsupported, report it. Do NOT edit any file: report, and the main session decides. Set edit_id to the proposed_edits.json id when the finding is about a résumé edit, otherwise "".
- Research claims (research.html, overview.html, questions.html): open each cited source. Report claims the source does not say, overstates or dates wrongly; claims with no source; inferences not labelled as inferences; anything about compensation.
- Score claims (score.html, mismatch.html, score.json): every quoted evidence line must exist in professional-journey.md or the cited case study at the cited place, and support the score given. Status words never upgraded (designed is not shipped, piloted is not production); no invented numbers; open claims left unresolved; the weights sum to 1.00 and the points reproduce weighted_total; the gates named separately.
- Every proposed résumé edit: old_text matches the master row (jobs_tracker_v2 resume_blocks, doc_key='master', same section_id and ord) exactly; every fact in new_text is supported by the cited journey line (quote it); 25 words or fewer; a strong, unique leading verb (check same-root collisions across the whole master, with the edit applied); a number or scale marker; a bold fact; no trailing period; acronyms expanded on first use; no invented number; no upgraded status word. The résumé-changes page must show exactly the proposed bullets.
- jd.html against jd.md: word for word. Report any word added, changed or dropped.
- Every page: the page contract (no <style>; no <script> before </main>; no {{…}} left; ids unique across the workspace; every link lands); every acronym expanded on first use.
In checked_and_sound, list only the claims most likely to be wrong that you checked and found sound.`
const check = await run(CHECK, { label: `agent 3 · adversarial check (${A.short})`, phase: 'Check', schema: C_SCHEMA })

return { agents_used: spawned, research, score, check }
