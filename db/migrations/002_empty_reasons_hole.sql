-- 002 — close the empty-array hole in "a move must have a reason".
--
--   psql -d v2_daily -f db/migrations/002_empty_reasons_hole.sql
--
-- 001 wrote `array_length(reasons, 1) >= 1`. For an EMPTY array array_length
-- returns NULL, not 0, and a CHECK constraint only rejects FALSE — NULL passes.
-- So `reasons = '{}'` satisfied a constraint whose entire purpose was to make a
-- reason mandatory. cardinality() returns 0 for an empty array — but NULL for a
-- NULL array, which is the SAME hole one step over, so it needs coalesce() too.
-- Both were reachable: '{}' and NULL each satisfied a mandatory-reason check.
BEGIN;

ALTER TABLE task_state DROP CONSTRAINT IF EXISTS task_state_moved_needs_reason;
ALTER TABLE task_state ADD  CONSTRAINT task_state_moved_needs_reason
  CHECK (moved IS NULL OR coalesce(cardinality(reasons), 0) >= 1);

ALTER TABLE task_event DROP CONSTRAINT IF EXISTS task_event_move_needs_reason;
ALTER TABLE task_event ADD  CONSTRAINT task_event_move_needs_reason
  CHECK (action NOT IN ('parked', 'pushed', 'dropped')
         OR coalesce(cardinality(reasons), 0) >= 1);

COMMIT;
