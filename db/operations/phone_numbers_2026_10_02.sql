-- His two phone numbers (2 Oct 2026): "+91 97049 68861 & +91 93640 27487"; he put both on the
-- master in Word as "+91 93640 27487 / +91 97049 68861" (with 93640 mistyped as 96340, which he
-- confirmed is wrong) and wants both everywhere. Master and the unsent seats only; sent seats are frozen.
-- Also the 2025-26 VoltusWave title, by his rule of 2 Oct 2026: "For IC roles, I want to use 'Principal Software Architect'
-- whilst for managerial roles let's use 'Vice President of Technology'". Astroum (he retitled it in Word) and Recruise are IC
-- seats; GetHyr (Engineering Manager) stays VP; Lilly already says Principal Software Architect.
-- Re-runnable: each UPDATE matches the old value only.
\set ON_ERROR_STOP on
BEGIN;
UPDATE resume_profile SET value_html = '+91 93640 27487 / +91 97049 68861'
 WHERE field_label = 'Phone' AND value_html = '+91 93640 27487'
   AND doc_key IN ('master',
                   'seat:astroum-ai-principal-lead-software-engineer',
                   'seat:gethyr-engineering-manager',
                   'seat:eli-lilly-sr-principal-engineer-ai-ml-integration',
                   'seat:recruise-ai-architect-healthcare');
UPDATE resume_roles SET role_title = 'Principal Software Architect'
 WHERE doc_key IN ('seat:astroum-ai-principal-lead-software-engineer', 'seat:recruise-ai-architect-healthcare')
   AND role_title = 'Vice President of Technology';
COMMIT;
