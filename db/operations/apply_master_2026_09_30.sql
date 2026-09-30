-- Master résumé updates, 30 Sep 2026 (his ask: "can we update master/Abhisheik_Deo_Resume.docx",
-- so the same file goes to Tachyon and to Naukri and other portals). Backup: variant:master-2026-09-30.
-- Sources: professional-journey.md "His answers, 30 September 2026"; journey 616 (VP title); the
-- interview-prep ledger's axe MCP line (his words, 10 Sep 2026: "Our CTO envisioned it. I built it and
-- deployed it to each enterprise customer"). The Anthropic arrangement and the MCP preview stay OFF the
-- résumé (his rule: interviews only). Guarded: each change applies only to the expected current text.
\set ON_ERROR_STOP on
BEGIN;
-- 1. Latest VoltusWave role title (journey 616: "Principal Software Architect / VP of Technology").
UPDATE resume_roles SET role_title = 'Vice President of Technology'
 WHERE doc_key = 'master' AND n = 1 AND role_title = 'Principal Software Architect';
-- 2. Python and FastAPI on the delivery bullet (journey 678; his 30 Sep answer, Python 2+).
UPDATE resume_blocks SET html = 'Delivered <strong>10 decision-intelligence services</strong> in Python and FastAPI on 4 query archetypes to production for ~10,000 patients, absorbing 20 review findings into one design'
 WHERE doc_key = 'master' AND section_id = 'quick-vp' AND ord = 3 AND text = 'Delivered 10 decision-intelligence services on 4 query archetypes to production for ~10,000 patients, absorbing 20 review findings into one design';
-- 3. The axe MCP server at Deque (new bullet, last in the role; 2024 per his 30 Sep answer).
INSERT INTO resume_blocks (doc_key, section_id, section_kind, ord, bullet_key, html)
SELECT 'master', 'quick-deque', 'experience', 16, 'deque-authored-axe-mcp-server',
       'Authored the <strong>axe Model Context Protocol (MCP) server</strong> in 2024, giving AI agents axe accessibility testing, and rolled it out to <strong>every enterprise customer</strong>'
 WHERE NOT EXISTS (SELECT 1 FROM resume_blocks WHERE doc_key = 'master' AND bullet_key = 'deque-authored-axe-mcp-server');
-- 4. CloudFormation (Deque and VoltusWave, his 30 Sep answer).
UPDATE resume_blocks SET html = '<strong>Terraform, AWS CloudFormation + Docker on AWS</strong> (company-wide standard, Elastic Container Service (ECS) Fargate)'
 WHERE doc_key = 'master' AND section_id = 'quick-skills-ee' AND ord = 5 AND html = '<strong>Terraform + Docker on AWS</strong> (company-wide standard, Elastic Container Service (ECS) Fargate)';
-- 5. Microservices since Teletext (2016) and REST since innRoad (2013), his 30 Sep answer.
UPDATE resume_blocks SET html = '<strong>Java + Spring Boot Microservices</strong> (Java 8/17, Spring Boot 2.x, JavaServer Pages, Versioned Application Programming Interfaces (APIs); microservices since 2016, representational state transfer (REST) since 2013)'
 WHERE doc_key = 'master' AND section_id = 'quick-skills-ee' AND ord = 2 AND html = '<strong>Java + Spring Boot Microservices</strong> (Java 8/17, Spring Boot 2.x, JavaServer Pages, Versioned Application Programming Interfaces (APIs))';
COMMIT;
