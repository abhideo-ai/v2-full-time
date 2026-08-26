# External review of Abhisheik_Deo_Resume.pdf — Keyloop Principal Architect

**Received:** 2026-08-26 · **Source:** pasted by Abhisheik, external reviewer/tool (origin not stated)
**Subject file:** `August-2026/26/keyloop-principal-architect/Abhisheik_Deo_Resume.pdf` (the v2 tailored
résumé, exported 2026-08-26 17:58, scored 89.6 technical)

> ⚠ This reviewer calls the file above "the original 3-page CV" and contrasts it with a
> "tailored resume" of their own (two `.docx` files). No such files were supplied. Read every
> "Original CV" row below as referring to OUR tailored Keyloop résumé.

Stored verbatim. Adjudication lives in `feedback-adjudication.html`.

---

KEYLOOP — PRINCIPAL ARCHITECT
Candidate: Abhisheik Deo
Date: 26 August 2026

========================================
1. VERDICT
========================================

Can I apply?  YES.

Technical match:  84 / 100
Hiring-manager range after a screen:  78–88
  (drops to mid-70s if they treat DMS/automotive as a hidden must-have)

This is a strong PLATFORM-ARCHITECT match and a weak DOMAIN match.
The JD is written as platform + AI first. Automotive is listed as nice-to-have.

Apply this week with the tailored resume + cover letter.
Do not apply with the original 3-page CV.

========================================
2. TECHNICAL MATCH BREAKDOWN
========================================

JD requirement                                         Weight   Score   Notes
-----------------------------------------------------  ------   -----   -----
15+ yrs, 5+ senior architecture                           12      95    19+ yrs; Deque Staff/Lead 2019-25; Principal 2025-26
Enterprise-scale architecture transformation              14      92    Per-customer -> shared SaaS; monolith -> 10-15 services; Keycloak -> SSO, zero disruption
Large-scale multi-tenant SaaS                             14      93    ~300 tenants; org-id + JWT; dedicated DBs for regulated banks
Cloud / distributed systems / platform engineering        12      88    AWS, K8s, Terraform, ECS, Kinesis, Lambda, Aurora, DynamoDB. Not proven at Keyloop transaction scale
Observability, SRE, cost                                   8      86    Datadog, error rate <3%, multi-AZ DR, 70% Spot, cost -25-30%, deploys <10 min
Data architecture                                         10      87    Event sourcing, CQRS, DynamoDB single-table, Parquet/DuckDB, Aurora, OpenSearch, Neptune
Executive communication / influence without authority      8      82    Design-doc discipline across 5 teams. No board-level / multi-region product-strategy proof
AI-native platform (agents, reusable infra, safety)       14      90    LangGraph runtime, 4 archetypes, in-VPC models, guardrails, Claude Code / Codex rollout
Nice-to-have: microservices / event-driven                 4      90    Production microservices + Kinesis + event-sourced spine
Nice-to-have: automotive retail / DMS                      3      15    Hotel, accessibility SaaS, healthcare, energy. Zero DMS / OEM / dealer
Nice-to-have: cloud certifications                         1       0    None listed

Weighted total ~ 84

What this means
- Clears every printed must-have except industry tenure.
- Over-indexes on "How we work with AI" - the rarest JD item.
- Under-indexes on automotive system-of-record scale (20k retailers, 80+ OEMs, ~215M monthly platform transactions).

What would move the number
- -> 90+: one Fusion-shaped case study ready for interview (multi-brand tenancy + shared API + event contract), even if the domain was healthcare/banking.
- -> mid-70s: if they treat DMS tenure as a hidden must-have.
- Certs add almost nothing at this level.

========================================
3. DOES THE RESUME MATCH THE JD?
========================================

Short answer
- YOU match the role.
- The ORIGINAL resume does not match the role's STORY.
- The TAILORED resume matches the required architecture. It still does not match domain or Keyloop scale. That is correct - do not fake those.

What already matches (keep)

JD line                                              Your evidence
---------------------------------------------------  ----------------------------------------------------------
15+ years, 5+ senior architecture                    19+ years; Deque Staff/Lead 2019-25; Principal 2025-26
Enterprise-scale transformation                      Per-customer -> shared SaaS; monolith -> 10-15 services; Keycloak -> central SSO, zero disruption
Large-scale multi-tenant SaaS                        ~300 instances; org-id + JWT; dedicated DBs for regulated banks
Cloud / distributed / platform                       AWS, K8s, Terraform, ECS, Kinesis, Aurora, DynamoDB
Observability, SRE, cost                             Datadog, <3% errors, 70% Spot, 25-30% cost down, deploys <10 min
Data architecture                                    Event sourcing, CQRS, Parquet/DuckDB, Neptune
Influence without authority                          Design docs across five teams; client-CEO-to-engineering
AI-native (orchestration, reusable infra, safety)    LangGraph, 4 archetypes, in-VPC models, claim grammar, Codex/Claude rollout
Microservices / event-driven (nice-to-have)          Yes, in production

========================================
4. WHERE THE ORIGINAL RESUME DOES NOT MATCH - AND WHY
========================================

1) It is a career archive, not a bid for this job
   JD wants: shape a product SaaS platform; set cross-cutting standards; influence product + engineering strategy.
   Original summary mixes banks, Keycloak, VoltusWave standards, LangGraph, and 9-10 years of PATIENT history.
   First 15 seconds read as "healthcare + Java + tools," not "principal of a multi-tenant product platform."
   Why it hurts: screeners and AI scoring dump off-domain nouns (PHI, GNN, Neptune, chronic care) before multi-tenant SaaS lands.

2) Domain - automotive retail / DMS / Fusion - missing
   Nice-to-have on the JD, first probe in interview.
   You have enterprise SaaS. You do not have dealer, OEM, vehicle inventory, aftersales, or a car system-of-record.
   Domains you do have: hotel (innRoad, Teletext), accessibility (Deque), healthcare (VoltusWave), energy (El Paso).
   Why it hurts: original CV never maps the transfer (shared platform APIs + tenant isolation + event spine ~ open automotive platform). The gap looks blank, not mapped.

3) Principal Architect IC posture is buried
   JD: senior IC reporting to Engineering Director; coach Architects; ROI on bets; influence without authority.
   Original: title soup (Principal / Lead SDE / Sr Staff / Staff / Co-Founder VP). Skills wall first. Full jobs back to 2007.
   Why it hurts: they are hiring one IC who owns platform bets, not a VP and not a staff engineer who shipped features.

4) AI is present but aimed at the wrong buyer
   JD wants: platform strategy for agent orchestration + reusable AI infra; safety standards that ENABLE delivery; architectural bets; AI-native from day one.
   Original shows: LangGraph, Llama 3.1, SageMaker embeddings, GNN on Neptune, "Claude Code + Codex under review," clinical workflows.
   Why it hurts: the operating model (runtime, guardrails, team rollout) is what they asked for. GNN/Neptune/chronic-care reads as product-ML in healthcare. "Under review" sounds unfinished.

5) Data sovereignty is healthcare-shaped, not platform-shaped
   You have the real capability: dedicated DBs for banks, PHI in client VPC, HIPAA, ISO 27001.
   Original names HIPAA and PHI repeatedly.
   Why it hurts: Keyloop's nouns are dealer/OEM residency, GDPR, multi-country DMS, multi-brand isolation. Untranslated PHI makes you look like a health-tech architect.

6) Developer experience is a bullet, not an outcome
   JD: champion DevEx and productivity as a PLATFORM-LEVEL outcome.
   You have: deploys <10 min, Jenkins -> GitHub Actions, 50% faster releases, Codex rollout.
   Original lists these under jobs/skills, mixed with Kinesis and Neptune.
   Why it hurts: they want "I treat DevEx as architecture," not "I improved CI/CD."

7) Build / buy / adopt and ROI are implied, not shown
   JD: evaluate emerging tech; strategic build/buy/adopt; ROI on major investments.
   Closest proof: in-house ELK vs licensed pricing (-46% opex); licence removal; Spot capacity.
   Missing: a framed recommendation, a rejected vendor, an investment case.
   Why it hurts: principals at this level are judged on decisions, not only systems built.

8) Cloud certifications - absent
   Nice-to-have. Rarely decides the hire at this seniority. Can decide a lazy first ATS pass.

9) Document craft works against ATS and humans
   - 3 pages; skills wall on page 1; experience starts late
   - Dense parentheticals (every acronym expanded)
   - Photo + decorative header on the original PDF
   - LinkedIn is a label, not a URL
   - Last role ended Apr 2026; as of Aug 2026 that is a 4-month gap with no "Present"
   Why it hurts: their JD says they use AI to flag inconsistencies. Unexplained gaps and off-domain keywords get scored.

10) Scale story does not meet their published numbers
    Keyloop shape: ~20k retailers, 80+ OEMs, ~215M platform transactions/month.
    Your shape: ~300 enterprise instances, 20+ API clients, 10 pipelines, 20 engineers.
    Same PATTERN, different magnitude.
    Why it hurts: original CV never says "pattern, not peer scale," so a reader either inflates you or dismisses you.

========================================
5. ORIGINAL CV vs TAILORED CV
========================================

Problem                         Original CV              Tailored CV
------------------------------  -----------------------  --------------------------------
Aimed at this JD                No                       Yes - title, profile, outcomes
Multi-tenant + standards first  Buried in prose          First screen
AI as platform + safety + team  Mixed with GNN/clinical  Explicit
Automotive gap                  Silent                   Named in the letter, not faked on the resume
2007-2015 noise                 Full jobs                One compressed block
Length                          3 pages                  2 pages

Remaining honest gaps after rewrite
- No DMS / automotive tenure
- No listed cloud cert
- Smaller published scale than Keyloop
- 4-month gap after Apr 2026
- No written build/buy/ROI case

========================================
6. APPLY / DO NOT APPLY
========================================

Apply if all of these are true
- You send the tailored resume + letter, not the original 3-page CV
- You can work a UK-overlapping shift (other Keyloop Hyderabad architect roles already require this)
- You can explain Apr-Aug 2026 in one sentence
- You will not pretend you have DMS tenure

Do not apply if
- You need this to be a domain-expert hire (it will not be)
- You cannot talk tenancy, event contracts, and AI guardrails without slides
- You are looking at Keyloop's OTHER Hyderabad Principal role (Infrastructure - Windows/AIX/VMware). That is not this job.

Location
- Keyloop hires Principal-level engineers in Hyderabad. Location is not a reason to sit this out.

Odds, plainly
- Worth submitting. Not a lock.
- If they want "has run a dealer platform," you lose.
- If they want "can own Fusion's architectural bets and the AI operating model," you are in the conversation.

========================================
7. WHAT TO SEND
========================================

Files
- Abhisheik_Deo_Keyloop_Principal_Architect_Resume.docx
- Abhisheik_Deo_Keyloop_Principal_Architect_Cover_Letter.docx

If the form has a "why you" box, paste this and stop:

I set multi-tenant SaaS and platform standards at a few-hundred-instance scale, including regulated carve-outs and zero-disruption identity migration. I also defined the AI runtime and safety rules a team actually used. I do not have DMS tenure. I do have the platform shape Fusion needs: shared instance, shared APIs, evented data spine, isolation that survives audit.

Interview one-liner
"Platform, tenancy, data spine, and AI operating model: high 80s. Automotive nouns: I will learn those in weeks, not years. That is the bet."

Gap one-liner (Apr 2026 - Aug 2026)
"The Principal role at VoltusWave ended in April. I have been selecting the next platform problem, not collecting titles."

Do not invent
- Automotive / DMS / dealer / OEM delivery
- Cloud certifications
- Keyloop-scale transaction volumes
- Current employment after April 2026
