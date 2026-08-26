-- 001 — one reason becomes several.
--
--   psql -d v2_daily -f db/migrations/001_reason_to_reasons.sql
--
-- A move-out often has more than one cause at once: the posting closed AND the
-- band came back below floor. Single-reason forced a choice between them and
-- pushed the rest into a free-text note nothing can count.
--
-- Idempotent: safe to run twice, and safe on a populated database — an existing
-- single reason becomes a one-element array rather than being dropped.
BEGIN;

ALTER TABLE task_state ADD COLUMN IF NOT EXISTS reasons text[];
ALTER TABLE task_event ADD COLUMN IF NOT EXISTS reasons text[];

UPDATE task_state SET reasons = ARRAY[reason]
 WHERE reason IS NOT NULL AND reasons IS NULL;
UPDATE task_event SET reasons = ARRAY[reason]
 WHERE reason IS NOT NULL AND reasons IS NULL;

ALTER TABLE task_state DROP COLUMN IF EXISTS reason;
ALTER TABLE task_event DROP COLUMN IF EXISTS reason;

-- A move-out with no reason is the thing this whole change exists to prevent,
-- so the database refuses it rather than trusting every caller to remember.
ALTER TABLE task_state DROP CONSTRAINT IF EXISTS task_state_moved_needs_reason;
ALTER TABLE task_state ADD  CONSTRAINT task_state_moved_needs_reason
  CHECK (moved IS NULL OR (reasons IS NOT NULL AND array_length(reasons, 1) >= 1));

ALTER TABLE task_event DROP CONSTRAINT IF EXISTS task_event_move_needs_reason;
ALTER TABLE task_event ADD  CONSTRAINT task_event_move_needs_reason
  CHECK (action NOT IN ('parked', 'pushed', 'dropped')
         OR (reasons IS NOT NULL AND array_length(reasons, 1) >= 1));

COMMIT;
