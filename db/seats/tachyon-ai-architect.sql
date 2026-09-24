-- db/seats/tachyon-ai-architect.sql
--
-- Rule 7 re-vectoring for ONE seat: AI Architect, Tachyon Technologies, Hyderabad.
-- Posting https://www.linkedin.com/jobs/view/4469298952/ - requisition TYI-4328.
-- REBUILT 2026-09-24. The 20 Sep build (application 115) was deleted by him along with its
-- workspace (migration 013); this file replaces that one wholesale. git has the old version.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/seats/tachyon-ai-architect.sql
--
-- Run ONCE, right after db/operations/clone_seat_resume.sql creates the seat document.
-- Not re-runnable: every UPDATE is pinned to the master wording it replaces and RAISES if
-- it matches anything other than exactly one row (the 20 Sep build had one UPDATE silently
-- match zero rows). The MASTER IS NEVER TOUCHED.
--
-- Per CLAUDE.md "Resume Writing Points", edits land only in the last five roles.
-- 16 proposed, two adversarial checks (quick-vp; the other four roles), adjudicated:
--   * vp-07 Reimagined CUT - the edit bolded PostgreSQL as VoltusWave's relational layer;
--     professional-journey.md:80 names only DynamoDB + OpenSearch for that stint, and
--     "P95 under 30 ms" has zero hits in either journey file. Master wording kept as is.
--   * vp-05 Instrumented FIXED - kq1:776 SPECIFIES a 100+ clinician-graded golden set as an
--     evaluation contract; nothing says it was labelled. Worded as "built to a contract".
--   * vp-10 FIXED - "Facilitated" overstated journey.md:218 ("we sat down with the client's
--     chief executive"); now "Co-defined".
--   * deque-01 FIXED - "moving" collided with Trimmed's mid-bullet "moving"; back to "migrating".
-- Open claims (graph neural network, four Rocket metrics, 70-80%, 27 ms / P95 16 ms,
-- 100,000-concurrent) are untouched. New bullets go into the AI cluster of quick-vp.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE v_doc text := 'seat:tachyon-ai-architect';
BEGIN
  IF NOT EXISTS (SELECT 1 FROM resume_documents WHERE doc_key = v_doc) THEN
    RAISE EXCEPTION 'REFUSING: % does not exist - run db/operations/clone_seat_resume.sql first', v_doc;
  END IF;
  IF (SELECT status::text FROM applications WHERE slug = 'tachyon-ai-architect')
     NOT IN ('new','recommended_apply','recommended_skip','resume_drafted','resume_finalized') THEN
    RAISE EXCEPTION 'REFUSING: this seat is past a pre-send state - a sent resume is never edited';
  END IF;
END $$;

-- ---------- content edits, in place, leading verbs preserved ----------
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Assembled a <strong>10-query</strong> decision-intelligence platform in <strong>Python (FastAPI, LangChain, LangGraph)</strong> on <strong>4 reusable archetypes</strong> — Retrieval, Cohort Aggregation, Sequence Mining, Graph Traversal$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND ord=10
     AND text = $q$Assembled a 10-query decision-intelligence platform on 4 reusable archetypes — Retrieval, Cohort Aggregation, Sequence Mining, Graph Traversal — on Amazon Neptune$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'vp-01 (Assembled) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Engineered a production retrieval-augmented generation (RAG) service on <strong>Elasticsearch dense_vector</strong> filtered nearest-neighbour search across <strong>80+ chronic conditions</strong>, keeping <strong>Amazon Neptune</strong> off the serving path$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND ord=7
     AND text = $q$Engineered a retrieval-augmented generation (RAG) pipeline on Elasticsearch dense_vector filtered nearest-neighbour search across 80+ chronic conditions, keeping Amazon Neptune off the serving path$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'vp-03 (Engineered) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Secured protected health information inside the client <strong>virtual private cloud</strong> by self-hosting embeddings and <strong>Llama 3.1 on Ollama</strong> for every model call$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND ord=13
     AND text = $q$Secured protected health information inside the client virtual private cloud by self-hosting embeddings and Llama 3.1 for every model call$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'vp-06 (Secured) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Formalised a <strong>Health Insurance Portability and Accountability Act (HIPAA)</strong> control framework across <strong>10 production pipelines</strong> — data protection, role-based access governance, audit trails for clinical workflows$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND ord=15
     AND text = $q$Formalised a Health Insurance Portability and Accountability Act (HIPAA) control framework across 10 production pipelines — data protection, access governance, audit trails for clinical workflows$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'vp-08 (Formalised) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Forged central identity in <strong>Spring Boot</strong>, migrating every instance from <strong>Keycloak</strong> to <strong>Red Hat single sign-on</strong> over <strong>OpenID Connect and OAuth 2.0</strong>, zero disruption$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-deque' AND ord=3
     AND text = $q$Forged central authentication in Java and Spring Boot, migrating every instance from Keycloak to Red Hat single sign-on — users, roles, client registrations, groups, zero disruption$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'deque-01 (Forged) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Championed decomposition of a monolith into <strong>10–15 microservices</strong>, splitting on independent scaling and database ownership rather than on team boundaries$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-deque' AND ord=7
     AND text = $q$Championed decomposition of a monolith into 10–15 services, splitting on independent scaling and database ownership rather than on team boundaries$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'deque-02 (Championed) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Anchored decomposition of the <strong>IBM Db2 Configuration Manager</strong> enterprise monolith into <strong>Java and Spring Boot</strong> microservices, defining service boundaries across <strong>z/OS mainframe</strong> and distributed platforms$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-rocket' AND ord=1
     AND text = $q$Anchored decomposition of the IBM Db2 Configuration Manager monolith into Java and Spring Boot microservices, defining boundaries across z/OS mainframe and distributed platforms$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'rocket-01 (Anchored) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Helmed end-to-end development, deployment and operations on containerised <strong>Amazon Elastic Container Service</strong>, setting the architectural roadmap <strong>every subsequent product</strong> worked from$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-voltuswave-cofounder' AND ord=3
     AND text = $q$Helmed end-to-end development, deployment and operations on Amazon Elastic Container Service, setting the architectural roadmap every subsequent product worked from$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'cofounder-01 (Helmed) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Codified parallel <strong>scatter-gather integration</strong> across <strong>25 hotel supplier APIs</strong> on a <strong>MuleSoft enterprise service bus</strong>, superseding <strong>.NET 2.0</strong> a prior team could not upgrade$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-teletext' AND ord=1
     AND text = $q$Codified a parallel scatter-gather across 25 hotel suppliers on a MuleSoft enterprise service bus, superseding a .NET 2.0 stack a prior team could not upgrade$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'teletext-01 (Codified) matched % rows, expected 1', n; END IF;
END $do$;
DO $do$ DECLARE n int; BEGIN
  UPDATE resume_blocks SET html = $q$Reconciled per-supplier hotel identifiers onto licensed <strong>GIATA MultiCodes</strong>, automating the pipeline on serverless <strong>AWS Lambda</strong> with <strong>human-in-the-loop approval</strong> retained, growing revenue <strong>8% month over month</strong>$q$
   WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-teletext' AND ord=3
     AND text = $q$Reconciled per-supplier hotel identifiers onto licensed GIATA MultiCodes, automating the pipeline on AWS Lambda with human approval retained, growing revenue 8% month over month$q$;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n <> 1 THEN RAISE EXCEPTION 'teletext-02 (Reconciled) matched % rows, expected 1', n; END IF;
END $do$;

-- ---------- new bullets (verbs stem-checked across the whole seat document) ----------
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
  VALUES ('seat:tachyon-ai-architect', 'quick-vp', 'experience', 900, 'vp-choreographed-a-deterministic-multi', $q$Choreographed a deterministic <strong>multi-agent LangGraph</strong> state graph live in production — <strong>3</strong> blind parallel finder agents behind a barrier that rejects hallucinated candidates$q$);
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
  VALUES ('seat:tachyon-ai-architect', 'quick-vp', 'experience', 901, 'vp-routed-precedent-search-model', $q$Routed precedent-search model calls between self-hosted <strong>Llama 3.1 8B</strong> and <strong>70B</strong> escalation, pausing gate-suppressed queries for durable <strong>human-in-the-loop</strong> review through LangGraph interrupts$q$);
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
  VALUES ('seat:tachyon-ai-architect', 'quick-vp', 'experience', 902, 'vp-instrumented-self-hosted-langsmith', $q$Instrumented self-hosted <strong>LangSmith</strong> tracing and an offline evaluation harness built to a <strong>100+ query</strong> clinician-graded golden-set contract, version-pinning every score to its dataset and model$q$);
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
  VALUES ('seat:tachyon-ai-architect', 'quick-vp', 'experience', 903, 'vp-projected-an-append-only', $q$Projected an append-only <strong>DynamoDB</strong> event spine, hydrated with <strong>9–10 years of patient history</strong>, through serverless <strong>AWS Lambda</strong> into an <strong>Amazon Neptune</strong> decision graph$q$);
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
  VALUES ('seat:tachyon-ai-architect', 'quick-vp', 'experience', 904, 'vp-co-defined-the-killer', $q$Co-defined the <strong>killer queries</strong> with the client's chief executive in AI discovery, separating production AI from a demo across <strong>80+ chronic conditions</strong>$q$);

-- ---------- quick-vp order: new bullets sit in the AI cluster ----------
UPDATE resume_blocks SET ord = ord + 1000 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp';
UPDATE resume_blocks SET ord = 1 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-architected-a-two-stream';
UPDATE resume_blocks SET ord = 2 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-spearheaded-the-complete-rewrite';
UPDATE resume_blocks SET ord = 3 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-scaled-a-go-chat';
UPDATE resume_blocks SET ord = 4 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-reimagined-the-data-layer';
UPDATE resume_blocks SET ord = 5 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-deployed-datadog-observability-across';
UPDATE resume_blocks SET ord = 6 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-delivered-patient-onboarding-off';
UPDATE resume_blocks SET ord = 7 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-engineered-a-retrieval-augmented';
UPDATE resume_blocks SET ord = 8 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-tuned-precedent-retrieval-on';
UPDATE resume_blocks SET ord = 9 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-pioneered-a-context-graph';
UPDATE resume_blocks SET ord = 10 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-co-defined-the-killer';
UPDATE resume_blocks SET ord = 11 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-assembled-a-10-query';
UPDATE resume_blocks SET ord = 12 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-choreographed-a-deterministic-multi';
UPDATE resume_blocks SET ord = 13 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-routed-precedent-search-model';
UPDATE resume_blocks SET ord = 14 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-instrumented-self-hosted-langsmith';
UPDATE resume_blocks SET ord = 15 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-instituted-event-sourcing-on';
UPDATE resume_blocks SET ord = 16 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-projected-an-append-only';
UPDATE resume_blocks SET ord = 17 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-sealed-multi-tenant-isolation';
UPDATE resume_blocks SET ord = 18 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-secured-protected-health-information';
UPDATE resume_blocks SET ord = 19 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-enforced-large-language-model';
UPDATE resume_blocks SET ord = 20 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-formalised-a-health-insurance';
UPDATE resume_blocks SET ord = 21 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-hardened-ten-production-analytics';
UPDATE resume_blocks SET ord = 22 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-extracted-confounder-gated-cohort';
UPDATE resume_blocks SET ord = 23 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-strengthened-statistical-rigour-across';
UPDATE resume_blocks SET ord = 24 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-distilled-patient-event-histories';
UPDATE resume_blocks SET ord = 25 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-recruited-engineering-from-0';
UPDATE resume_blocks SET ord = 26 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-brokered-company-wide-adoption';
UPDATE resume_blocks SET ord = 27 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-published-react-native-applications';
UPDATE resume_blocks SET ord = 28 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-provisioned-amazon-web-services';
UPDATE resume_blocks SET ord = 29 WHERE doc_key='seat:tachyon-ai-architect' AND section_id='quick-vp' AND bullet_key='vp-drove-a-measured-claude';

COMMIT;
