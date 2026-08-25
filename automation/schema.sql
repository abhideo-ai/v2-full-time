-- Daily-log state for the v2 full-time workspace.
--
--   createdb v2_daily
--   psql -d v2_daily -f automation/schema.sql
--
-- Two tables on purpose. task_state is the CURRENT state the page renders and
-- is what a GET returns. task_event is the append-only history — every tick,
-- untick, park, push and drop, with its reason. The history is the whole point
-- of using a database here: "how long did a task sit before it was done" is a
-- time-series question, and built-to-sent latency is the number that killed v1.

CREATE TABLE IF NOT EXISTS task_state (
  key        text PRIMARY KEY,
  day        date        NOT NULL,
  task_id    text        NOT NULL,
  done       boolean     NOT NULL DEFAULT false,
  done_at    timestamptz,
  moved      text,
  reason     text,
  note       text,
  until      date,
  moved_at   timestamptz,
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT task_state_moved_valid
    CHECK (moved IS NULL OR moved IN ('parked', 'pushed', 'dropped')),
  -- A push without a return date is just a park wearing a different label.
  CONSTRAINT task_state_pushed_needs_until
    CHECK (moved IS DISTINCT FROM 'pushed' OR until IS NOT NULL),
  -- The page builds the key as "<day>::<task id>"; keep the DB honest about it
  -- so a malformed key can never split a task's history in two.
  CONSTRAINT task_state_key_shape
    CHECK (key = day::text || '::' || task_id)
);

CREATE TABLE IF NOT EXISTS task_event (
  id      bigserial PRIMARY KEY,
  key     text        NOT NULL,
  day     date        NOT NULL,
  task_id text        NOT NULL,
  action  text        NOT NULL,
  reason  text,
  note    text,
  until   date,
  at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT task_event_action_valid
    CHECK (action IN ('done', 'undone', 'parked', 'pushed', 'dropped', 'restored'))
);

CREATE INDEX IF NOT EXISTS task_event_key_at_idx ON task_event (key, at DESC);
CREATE INDEX IF NOT EXISTS task_event_at_idx     ON task_event (at DESC);
