-- 013_delete_tachyon_seat.sql — jobs_tracker_v2
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/migrations/013_delete_tachyon_seat.sql
--
-- He deleted the workspace September-2026/20/tachyon-ai-architect/ and asked,
-- 2026-09-24: "Can you remove the entry from db as well?"
--
-- The seat was never sent (status resume_drafted, applied_at null), so the
-- freeze on sent seats does not apply. What goes:
--
--   applications id 115 (tachyon-ai-architect, Tachyon Technologies, fit 90)
--     -> CASCADE: application_events 36-39 (the only child rows it had)
--   resume_documents 'seat:tachyon-ai-architect'
--     -> CASCADE: 15 sections, 95 blocks, 10 roles, 4 profile, 2 education rows
--
-- Idempotent: a second run deletes nothing.
--
-- ⚠ PINNED TO THE OLD ROWS. He re-pasted the same posting the same day and the
-- seat was rebuilt under the SAME slug, so matching on slug alone would delete
-- the new build on a re-run. The application is pinned to id 115 and the seat
-- document to its 2026-09-20 timestamp.

begin;

delete from resume_documents
 where doc_key = 'seat:tachyon-ai-architect'
   and updated_at < '2026-09-24';

delete from applications
 where id = 115
   and slug = 'tachyon-ai-architect'
   and status = 'resume_drafted'
   and applied_at is null;

commit;
