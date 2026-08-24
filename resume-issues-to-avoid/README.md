# Resume Issues To Avoid

Source: distilled from two rounds of ATS resume-review screenshots that previously lived in this directory. **First round** produced the original 6 failure patterns. **Second round (2026-06-06)** evaluated the 17-bullet AI-centric VoltusWave VP section after the Killer-Query depth was folded in (0 Poor / 11 Okay / 21 Great out of 32 bullets) and surfaced 3 new findings about how this specific ATS tool scores.

Use this checklist when drafting or reviewing `resume_paste.html`, exported PDFs, and master-resume hygiene changes. The hard rules below combine both rounds.

## Hard Rules

- Keep every resume bullet at **25 words or fewer**.
- Every bullet should include at least **one number, percentage, scale marker, or measurable outcome**.
- Every bullet should include at least **one bolded/highlighted fact** in the paste source.
- **Bold must survive PDF export.** Visually verify the exported PDF — some "Print to PDF" pipelines strip `<strong>` formatting and the ATS reads the result as plain text. Use "Save as PDF" (not Print) and confirm bold characters are visibly heavier in the rendered PDF before uploading. *(New, second round.)*
- Start every bullet with a **strong action verb**.
- Keep leading verbs unique across the resume; same-root variants count as duplicates.
- **Per-bullet hygiene is evaluated independently.** Don't rely on cross-bullet acronym expansion — even if `GNN` was expanded in bullet 2, bullet 12 containing `GNN` will still get flagged on its own. Minimise acronyms per bullet; one acronym per bullet is the practical cap. *(New, second round.)*
- Do **not** end bullet points with periods.
- Expand acronyms on first use in resume reading order — **and consider re-expanding in later bullets** where this specific ATS rescans per-bullet.
- Do not rely on a bullet being merely true; it must be scan-friendly, quantified, and role-relevant.

## ATS Scoring Methodology (Second-Round Discovery)

The ATS evaluates **every bullet in the resume independently** and assigns each a category:

- **Great** — passes the hygiene gate (lead verb, quantified, bolded fact, no orphaned acronym, ≤25 words, no trailing period).
- **Okay** — at least one warning fires. Common Okay-bullet triggers (from the second-round run): no bold visible in the PDF, an acronym present, OR no metric.
- **Poor** — multiple hard-rule violations stacked.

A 17-bullet recent-role section with 11 Okay bullets is the failure mode the second round caught. Goal: every bullet in your current and previous role should fall in **Great**. Older roles can absorb the occasional Okay without tanking the overall score.

## Specific Failure Patterns From The Screenshots

### 1. Overlong Context Graph Bullet

Problem example:

`Architecting Context Graph, the core healthcare-AI decision intelligence layer for a virtual care platform treating 80+ chronic conditions — built on DynamoDB event spine, Amazon Neptune graph, and GNN models in training, exposed through a structured decision framework and a real-time adherence system.`

Issues:

- Too long
- Ends with a period
- Acronyms not expanded (`AI`, `GNN`)

Fix pattern:

`Architecting **Context Graph** on Amazon Neptune + Graph Neural Network (GNN) models for **80+ conditions**, with decision schemas and real-time adherence primitives`

### 2. Overlong Engineering-Org Bullet

Problem example:

`Built and scaled engineering organization from 0 to 20+ engineers across backend (Go, Python, Node.js), React Native, React, AI/Graph, and DevOps — exactly the shape a doctor-centric platform with mobile + web + AI + integrations needs`

Issues:

- Too long
- No bolded/highlighted fact
- Acronyms not expanded

Fix pattern:

`Grew engineering from 0 to **20+ engineers** across backend, mobile, web, Artificial Intelligence (AI), and DevOps`

### 3. Overlong Data-Platform Bullet

Problem example:

`Migrated PostgreSQL to AWS RDS and adopted Infrastructure as Code (CloudFormation) — cut daily backup time 3–4 hours, deployment errors 40%, and set the data-platform foundation a 0→1 startup needs from day 1.`

Issues:

- Too long
- No bolded/highlighted fact
- Ends with a period
- Acronyms not expanded (`AWS`, `RDS`)

Fix pattern:

`Migrated PostgreSQL to **Amazon Web Services (AWS) RDS**, cutting backup time **3-4 hours** and deployment errors **40%**`

### 4. Unquantified Mentorship Bullet

Problem example:

`Mentored engineers on scalable API design, code quality standards, documentation, and engineering best practices`

Issues:

- No number or measurable outcome
- No bolded/highlighted fact
- Acronym not expanded (`API`)

Fix pattern:

`Raised API quality standards across a **20+ tenant SaaS**, mentoring engineers on documentation, code review, and scalable contracts`

### 5. Unquantified Managed-Operations Bullet

Problem example:

`Managed end-to-end development, deployment, and operations on AWS Elastic Container Service, delivering highly scalable solutions that won early enterprise clients`

Issues:

- No number or measurable outcome
- No bolded/highlighted fact
- Acronym not expanded (`AWS`)
- Weak/generic opening verb for senior architecture resumes

Fix pattern:

`Delivered **0-to-1 platform operations** on Amazon Web Services (AWS) ECS, supporting early enterprise-client wins`

### 6. Weak Verb + Unquantified ELK Bullet

Problem example:

`Replaced third-party product with in-house ELK Stack solution, significantly reducing operational costs`

Issues:

- No number or measurable outcome
- No bolded/highlighted fact
- Weak opening verb
- Acronym not expanded (`ELK`)

Fix pattern:

`Implemented in-house Elasticsearch, Logstash, and Kibana (ELK) observability, reducing vendor dependency and operational cost`

If there is no real metric for cost reduction, use this bullet sparingly or drop it from tailored resumes.

### 7. Gerund Lead Verb ("Standing up …") — Second Round

Problem example:

`Standing up Health Insurance Portability and Accountability Act (HIPAA) framework across 10 production pipelines — data protection, access governance, audit trails for clinical workflows`

Issues:

- Lead phrase is a gerund (`Standing up`), not a recognised power verb
- ATS flags it generically as "needs a power verb"

Fix pattern:

`Established **Health Insurance Portability and Accountability Act (HIPAA)** framework across **10 production pipelines** — data protection, access governance, audit trails for clinical workflows`

Use recognised power verbs (Established, Built, Launched, Instituted, Delivered, Spearheaded, Drove, Owned, Architected, Designed, Scaled) over gerunds and uncommon-but-fresh verbs on the **most-prominent role**. Save uncommon-fresh verbs (Codified, Productized, Stewarded, Anchored, Helmed) for older roles where ATS scoring weight is lower.

### 8. Acronym-Dense Bullet — Second Round

Problem example:

`Orchestrated multi-tenant isolation defense-in-depth — TraversalSource wrapper + parquet partition + runtime assertion + per-tenant Neptune for Protected Health Information (PHI) tier`

Issues:

- Bullet contains one acronym (`PHI`) — flagged even though expanded inline
- Second-round ATS rescans per-bullet, so `PHI` alone earns the acronym warning

Fix pattern:

Either drop the acronym and spell it out, OR accept the acronym hit if it's load-bearing. Don't add MORE acronyms hoping the expansion saves you — the ATS will flag each one.

`Orchestrated **multi-tenant SaaS isolation** across **10 production pipelines** — TraversalSource wrapper, parquet partition, runtime assertion, per-tenant Neptune for health-data tier`

### 9. Bold Stripped By PDF Export — Second Round

Problem: every bullet in `resume_paste.html` carries `<strong>` tags around the bolded facts. After exporting to PDF, the rendered text reads flat — no visible bold.

Issues:

- ATS sees plain text and flags every bullet with the "no bolded fact" warning
- Score craters even though the source HTML is hygienically correct

Fix pattern:

- Use **Save as PDF** (Google Docs → File → Download → PDF; Word → Save As → PDF) instead of **Print to PDF** in the browser.
- Open the exported PDF in a viewer (Preview, Adobe Reader). Confirm the bolded facts are visually heavier than surrounding text.
- If bold is missing, the export pipeline stripped it. Switch tools (try `wkhtmltopdf`, LibreOffice headless export, or paste through Google Docs first then export).

## Review Checklist Before Export

- No bullet exceeds 25 words.
- No bullet ends with a period.
- Every bullet has a number or measurable scale marker.
- Every bullet has a bolded fact in `resume_paste.html` — AND the **exported PDF** visually shows that bold. *(Second-round addition.)*
- Each bullet uses at most **one acronym** — even properly-expanded ones earn an ATS flag per-bullet. *(Second-round addition.)*
- The lead verb is on the standard ATS power-verb whitelist for the **most-prominent role** (avoid `Standing up`, `Codified`, `Productized`, `Anchored`, `Helmed`, `Stewarded` on the current job; save those for older roles). *(Second-round addition.)*
- Every acronym is expanded on first use in resume reading order: examples include Artificial Intelligence (AI), Graph Neural Network (GNN), Amazon Web Services (AWS), Elastic Container Service (ECS), Relational Database Service (RDS), Elasticsearch / Logstash / Kibana (ELK), Red Hat Enterprise Linux (RHEL), Quality Assurance (QA), Representational State Transfer (REST), Health Insurance Portability and Accountability Act (HIPAA), Protected Health Information (PHI), Large Language Model (LLM).
- No screenshot problem bullet appears verbatim in a paste source.
- Weak openers like `Managed`, `Replaced`, `Responsible for`, `Worked on`, and `Helped` are replaced with outcome verbs.
- Run a second-round ATS check on the final exported PDF before uploading to a profile board. *(Second-round addition.)*
