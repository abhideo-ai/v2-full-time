-- db/seats/tachyon-ai-architect.sql
--
-- Rule 7 re-vectoring for ONE seat: AI Architect, Tachyon Technologies, Hyderabad.
-- Posting https://www.linkedin.com/jobs/view/4469298952 - requisition TYI-4328.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/seats/tachyon-ai-architect.sql
--
-- Run AFTER db/operations/clone_seat_resume.sql has created doc_key 'seat:tachyon-ai-architect'.
-- The MASTER IS NEVER TOUCHED - every statement below is scoped to the seat document.
--
-- WHY THESE EDITS: the binding constraint on this JD was never capability, it was the
-- resume surface. Across all 64 experience bullets the words agent, agentic, multi-agent,
-- LangChain, LangGraph, Python and FastAPI appeared ZERO times - all of them lived in one
-- skills label - while KQ10 is a shipped, production-deployed deterministic multi-agent
-- LangGraph orchestrator. CLAUDE.md records that exact shape (top-of-resume-only tailoring)
-- producing ZERO CALLS in June 2026.
--
-- Every edit keeps its leading verb. Two new bullets use verbs verified stem-free against
-- the whole document: Choreographed and Routed. The stem 'orchestrat' is BURNT because
-- Orchestrated already leads quick-deque #10 - a same-root collision CLAUDE.md records
-- having to fix once before.
--
-- TWO PROPOSED EDITS WERE REJECTED by majority adversarial vote and are NOT applied:
--   * adding 'Role-Resolved Enterprise Search' to the RAG skills line (2 of 3 refuted)
--   * reordering the LLM Productionisation skills line (3 of 3 refuted)
-- quick-vp 'Enforced large language model narrative guardrails' is deliberately UNTOUCHED:
-- whether those guardrails shipped is an open claim only he settles, and its 'designed to
-- reject' wording is the correct hedge.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE v_doc text := 'seat:tachyon-ai-architect'; v_n integer;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_doc) THEN
    RAISE EXCEPTION 'REFUSING: % does not exist - run db/operations/clone_seat_resume.sql first', v_doc;
  END IF;
  IF (SELECT status::text FROM applications WHERE slug = 'tachyon-ai-architect')
     IN ('applied','heard_back','not_selected','withdrawn') THEN
    RAISE EXCEPTION 'REFUSING: this seat has already been sent - a sent resume is never edited';
  END IF;
END $$;

-- ---------- content edits, in place, leading verbs preserved ----------
UPDATE resume_blocks SET html = $q$Assembled a <strong>10-query</strong> decision-intelligence platform in <strong>Python (FastAPI, LangChain, LangGraph)</strong> on <strong>4 reusable archetypes</strong> — Retrieval, Cohort Aggregation, Sequence Mining, Graph Traversal$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-assembled-a-10-query';
UPDATE resume_blocks SET html = $q$Engineered a production retrieval-augmented generation (RAG) service on <strong>Elasticsearch dense_vector</strong> filtered nearest-neighbour search across <strong>80+ chronic conditions</strong>, keeping <strong>Amazon Neptune</strong> off the serving path$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-engineered-a-retrieval-augmented';
UPDATE resume_blocks SET html = $q$Secured protected health information inside the client <strong>virtual private cloud</strong> by self-hosting embeddings, <strong>Llama 3.1 on Ollama</strong> for every model call, and <strong>LangSmith</strong> tracing$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-secured-protected-health-information';
UPDATE resume_blocks SET html = $q$Reimagined the data layer across <strong>relational PostgreSQL</strong>, <strong>NoSQL DynamoDB</strong> and <strong>OpenSearch</strong> with partition-key and indexing design holding <strong>P95 under 30 ms</strong> at 100,000-user load$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-reimagined-the-data-layer';
UPDATE resume_blocks SET html = $q$Reconciled per-supplier hotel identifiers onto licensed <strong>GIATA MultiCodes</strong>, automating the pipeline on <strong>AWS Lambda</strong> with <strong>human-in-the-loop approval</strong> retained, growing revenue <strong>8% month over month</strong>$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-teletext' AND bullet_key='teletext-reconciled-per-supplier-hotel';
UPDATE resume_blocks SET html = $q$Exposed shared platform application programming interfaces to <strong>280 axe Monitor clients</strong> — third-party Jira integration, <strong>versioned APIs</strong>, backward compatibility, customer-specific frontends on one <strong>Spring Boot</strong> backend$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-deque' AND bullet_key='deque-exposed-shared-platform-application';
UPDATE resume_blocks SET html = $q$Piloted <strong>Master Data Management (MDM)</strong> across <strong>2 countries</strong> — United States and Canada — integrating employee records from <strong>every store</strong> into one governed <strong>SQL Server</strong> hub$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='p-mcd' AND bullet_key='mcd-piloted-master-data-management';
UPDATE resume_blocks SET html = $q$Hands-on principal architect, <strong>19+ years</strong>. Built <strong>ten analytics and artificial intelligence (AI) services in Python</strong> on Amazon Web Services (AWS) for chronic care, end to end: a production <strong>deterministic multi-agent LangGraph</strong> service, <strong>retrieval-augmented generation (RAG)</strong> on Elasticsearch, causal inference and leakage-safe machine learning over <strong>9&ndash;10 years of patient history</strong>, a <strong>graph neural network (GNN)</strong> context graph, and self-hosted <strong>large language models (LLMs)</strong> inside the client boundary. Under that, about <strong>11 years of Java across three eras</strong>, from server-side Java in 2008 to <strong>Spring Boot 2.x on Java 8/17</strong> through February 2025. Consolidated per-customer deployments onto shared <strong>multi-tenant</strong> software as a service (SaaS) infrastructure, with dedicated isolation for regulated banking customers. Rewrote a chat platform's core service from <strong>Node.js to Go</strong> behind a two-stream <strong>Amazon Kinesis</strong> design, multi-availability-zone with failover and disaster recovery for <strong>Health Insurance Portability and Accountability Act (HIPAA)</strong> certification. Standardised the organisation on <strong>Kubernetes and Terraform</strong>, cutting infrastructure cost <strong>25&ndash;30%</strong> and deploy time to <strong>under 10 minutes</strong>.$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-summary' AND bullet_key='summary-hands-on-principal-architect';
UPDATE resume_blocks SET html = $q$<strong>Self-Hosted Models In-Virtual Private Cloud</strong> (Ollama, Llama 3.1, Self-Hosted LangSmith Tracing &amp; Evaluation)$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-ee' AND bullet_key='skills-ee-self-hosted-models-in';
UPDATE resume_blocks SET html = $q$<strong>Python AI Services</strong> (FastAPI, LangChain, LangGraph, Pydantic Structured Output, Model Context Protocol Servers)$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-ee' AND bullet_key='skills-ee-python-ai-services-fastapi';
UPDATE resume_blocks SET html = $q$<strong>Decision-Intelligence Platforms</strong> (Event-Sourced + Graph + AI, <strong>4 Reusable Archetypes</strong>)$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-tls' AND bullet_key='skills-tls-decision-intelligence-platforms-event';
UPDATE resume_blocks SET html = $q$Cross-Team Technical Leadership (<strong>6 sub-teams</strong>, company-wide standards, design-doc discipline)$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-tls' AND bullet_key='skills-tls-cross-team-technical-leadership';
UPDATE resume_blocks SET html = $q$Hands-on Principal Architect · 19+ yrs · Agentic AI: LangGraph, RAG, Self-Hosted LLMs · Graph + GNN · AWS, Kubernetes, Terraform · Multi-tenant SaaS · Java + Spring Boot (11 yrs) · HIPAA, ISO 27001 · AI-Leveraged Delivery (Claude Code + OpenAI Codex)$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-headline' AND bullet_key='headline-hands-on-principal-architect';
UPDATE resume_blocks SET html = $q$Codified the <strong>scatter-gather integration pattern</strong> across <strong>25 hotel supplier APIs</strong> on a <strong>MuleSoft enterprise service bus</strong>, superseding <strong>.NET 2.0</strong> a prior team could not upgrade$q$
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-teletext' AND bullet_key='teletext-codified-a-parallel-scatter';

-- ---------- new bullets ----------
-- Guarded against re-runs: after the re-order below these rows no longer sit at ord 900,
-- so a bare INSERT would not hit the primary key and would silently duplicate the bullet.
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
SELECT 'seat:tachyon-ai-architect','quick-vp','experience',900,'vp-choreographed-a-deterministic-multi-agent',$q$Choreographed a deterministic <strong>multi-agent LangGraph state graph</strong> live in production — <strong>3</strong> blind parallel finder agents behind a barrier that re-verifies every candidate$q$
 WHERE NOT EXISTS (SELECT 1 FROM resume_blocks WHERE doc_key='seat:tachyon-ai-architect'
                     AND section_id='quick-vp' AND bullet_key='vp-choreographed-a-deterministic-multi-agent');
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
SELECT 'seat:tachyon-ai-architect','quick-vp','experience',901,'vp-routed-every-chat-message',$q$Routed every chat message through <strong>serverless</strong> Simple Queue Service and <strong>AWS Lambda</strong> appending to <strong>Simple Storage Service (S3)</strong> objects read by web and mobile$q$
 WHERE NOT EXISTS (SELECT 1 FROM resume_blocks WHERE doc_key='seat:tachyon-ai-architect'
                     AND section_id='quick-vp' AND bullet_key='vp-routed-every-chat-message');
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
SELECT 'seat:tachyon-ai-architect','quick-skills-ee','skills',900,'skills-ee-agentic-multi-agent-ai-systems',$q$<strong>Agentic &amp; Multi-Agent AI Systems</strong> (Deterministic LangGraph StateGraph, Compiled Graph Runtime, Typed Durable State)$q$
 WHERE NOT EXISTS (SELECT 1 FROM resume_blocks WHERE doc_key='seat:tachyon-ai-architect'
                     AND section_id='quick-skills-ee' AND bullet_key='skills-ee-agentic-multi-agent-ai-systems');
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
SELECT 'seat:tachyon-ai-architect','quick-skills-bd','skills',900,'skills-bd-enterprise-integration-patterns',$q$<strong>Enterprise Integration Patterns</strong> (MuleSoft Enterprise Service Bus across <strong>25 hotel suppliers</strong>, Jira, versioned external APIs)$q$
 WHERE NOT EXISTS (SELECT 1 FROM resume_blocks WHERE doc_key='seat:tachyon-ai-architect'
                     AND section_id='quick-skills-bd' AND bullet_key='skills-bd-enterprise-integration-patterns');

-- ---------- re-order quick-vp: AI and cloud evidence to the head of the role ----------
-- Ordering is pure tailoring: no bullet text changes, and no bullet is dropped.
-- ord is part of the primary key, so shift the whole section clear of the target
-- range first; assigning 1..N directly collides with rows that still hold those ords.
UPDATE resume_blocks SET ord = ord + 1000
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp';
UPDATE resume_blocks SET ord=1 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-assembled-a-10-query';
UPDATE resume_blocks SET ord=2 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-choreographed-a-deterministic-multi-agent';
UPDATE resume_blocks SET ord=3 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-engineered-a-retrieval-augmented';
UPDATE resume_blocks SET ord=4 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-pioneered-a-context-graph';
UPDATE resume_blocks SET ord=5 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-provisioned-amazon-web-services';
UPDATE resume_blocks SET ord=6 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-architected-a-two-stream';
UPDATE resume_blocks SET ord=7 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-secured-protected-health-information';
UPDATE resume_blocks SET ord=8 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-tuned-precedent-retrieval-on';
UPDATE resume_blocks SET ord=9 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-spearheaded-the-complete-rewrite';
UPDATE resume_blocks SET ord=10 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-scaled-a-go-chat';
UPDATE resume_blocks SET ord=11 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-reimagined-the-data-layer';
UPDATE resume_blocks SET ord=12 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-routed-every-chat-message';
UPDATE resume_blocks SET ord=13 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-deployed-datadog-observability-across';
UPDATE resume_blocks SET ord=14 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-delivered-patient-onboarding-off';
UPDATE resume_blocks SET ord=15 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-instituted-event-sourcing-on';
UPDATE resume_blocks SET ord=16 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-sealed-multi-tenant-isolation';
UPDATE resume_blocks SET ord=17 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-enforced-large-language-model';
UPDATE resume_blocks SET ord=18 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-formalised-a-health-insurance';
UPDATE resume_blocks SET ord=19 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-hardened-ten-production-analytics';
UPDATE resume_blocks SET ord=20 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-extracted-confounder-gated-cohort';
UPDATE resume_blocks SET ord=21 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-strengthened-statistical-rigour-across';
UPDATE resume_blocks SET ord=22 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-distilled-patient-event-histories';
UPDATE resume_blocks SET ord=23 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-drove-a-measured-claude';
UPDATE resume_blocks SET ord=24 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-recruited-engineering-from-0';
UPDATE resume_blocks SET ord=25 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-brokered-company-wide-adoption';
UPDATE resume_blocks SET ord=26 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-published-react-native-applications';

-- ---------- promote the new agentic skills label to the head of Engineering Excellence ----------
UPDATE resume_blocks SET ord = ord + 1000
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-ee';
UPDATE resume_blocks SET ord = ord - 999
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-ee' AND ord < 1900;
UPDATE resume_blocks SET ord = 1
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-ee'
    AND bullet_key='skills-ee-agentic-multi-agent-ai-systems';
UPDATE resume_blocks SET ord = (SELECT max(ord)+1 FROM resume_blocks
      WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-bd' AND ord < 900)
  WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-skills-bd'
    AND bullet_key='skills-bd-enterprise-integration-patterns';
-- quick-skills-bd needs no offset: the new row lands strictly above the existing max.

-- ---------- prove it ----------
DO $$
DECLARE v_dupes integer; v_long integer; v_orch integer; v_blocks integer; v_diff integer;
BEGIN
  SELECT count(*) INTO v_blocks FROM resume_blocks
    WHERE doc_key='seat:tachyon-ai-architect' AND retired_at IS NULL;
  SELECT count(*) INTO v_dupes FROM (
    SELECT b.leading_verb FROM resume_blocks b JOIN resume_sections s
      ON s.doc_key=b.doc_key AND s.section_id=b.section_id
     WHERE b.doc_key='seat:tachyon-ai-architect' AND s.section_kind='experience'
       AND b.retired_at IS NULL GROUP BY 1 HAVING count(*)>1) d;
  SELECT count(*) INTO v_long FROM resume_blocks b JOIN resume_sections s
      ON s.doc_key=b.doc_key AND s.section_id=b.section_id
     WHERE b.doc_key='seat:tachyon-ai-architect' AND s.section_kind='experience'
       AND b.retired_at IS NULL AND b.word_count > 25;
  SELECT count(*) INTO v_orch FROM resume_blocks
     WHERE doc_key='seat:tachyon-ai-architect' AND retired_at IS NULL
       AND text ~* 'orchestrat' AND section_id <> 'quick-deque';
  IF v_dupes > 0 THEN RAISE EXCEPTION 'duplicate leading verbs: %', v_dupes; END IF;
  IF v_long  > 0 THEN RAISE EXCEPTION 'bullets over 25 words: %', v_long; END IF;
  IF v_orch  > 0 THEN RAISE EXCEPTION 'orchestrat stem collision outside quick-deque: %', v_orch; END IF;
  SELECT count(*) INTO v_diff FROM (
    SELECT coalesce(m.section_id,x.section_id) sid, coalesce(m.bullet_key,x.bullet_key) bk
      FROM (SELECT * FROM resume_blocks WHERE doc_key='master' AND retired_at IS NULL) m
      FULL OUTER JOIN (SELECT * FROM resume_blocks
                        WHERE doc_key='seat:tachyon-ai-architect' AND retired_at IS NULL) x
        ON x.section_id=m.section_id AND x.bullet_key=m.bullet_key
     WHERE m.html IS DISTINCT FROM x.html) d;
  -- ⚠ A ZERO-ROW UPDATE IS A SUCCESSFUL STATEMENT IN SQL AND WILL NOT ERROR. One edit here
  -- silently matched nothing because its bullet_key had been transcribed from a listing
  -- truncated to 44 characters. The count of statements written is never evidence that the
  -- edits landed - only a diff against the database is. Hence this assertion.
  IF v_diff <> 18 THEN
    RAISE EXCEPTION 'expected 18 blocks to differ from master, found % - an edit did not land', v_diff;
  END IF;
  RAISE NOTICE 'OK - % blocks, % differ from master, 0 dupe verbs, 0 over-length, 0 stem collisions',
               v_blocks, v_diff;
END $$;

COMMIT;
