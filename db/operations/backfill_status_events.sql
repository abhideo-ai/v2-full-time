-- db/operations/backfill_status_events.sql
--
-- Repair: a seat whose status was moved by a BARE UPDATE, so no status_events row
-- was ever written. Adds the missing row, dated to the seat's own applied_at.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 -f db/operations/backfill_status_events.sql
--
-- Takes no arguments: it finds every applied seat that has no 'applied' status event
-- and repairs all of them. Read-only in effect when there is nothing to repair.
--
-- WHY THIS EXISTS. On 2026-08-26 keyloop-principal-architect and
-- conde-nast-principal-engineer were moved to 'applied' with
--
--     update applications set status='applied', applied_at=now() where slug in (...)
--
-- instead of db/operations/mark_applied.sql. The status landed; the history did not.
-- mark_applied.sql says exactly why that matters in its own header: it "writes the
-- status_events row by hand, which a bare UPDATE would forget -- and that history is
-- how 'when did this go out' survives." Six seats had the row, two did not, and
-- nothing in verify.sql would ever have said so.
--
-- ⚠ THE REAL FIX IS NOT THIS FILE. It is using mark_applied.sql / withdraw.sql for
-- every status change. This exists because the damage was already done and because
-- the next person to hand-write an UPDATE will do it again.
--
-- Note the timestamp choice: applied_at, NOT now(). The event records when the seat
-- actually went out, not when the repair ran. A backfill that stamps itself with the
-- moment of repair destroys the one fact it was written to preserve -- the same
-- reasoning as the README's "`updated_at` is never collateral damage".

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_row   record;
    v_fixed integer := 0;
BEGIN
    FOR v_row IN
        SELECT a.id, a.slug, a.applied_at
          FROM applications a
         WHERE a.status = 'applied'
           AND NOT EXISTS (
                 SELECT 1 FROM status_events e
                  WHERE e.application_id = a.id
                    AND e.status = 'applied')
         ORDER BY a.applied_at NULLS LAST, a.slug
    LOOP
        IF v_row.applied_at IS NULL THEN
            RAISE EXCEPTION
              'seat % is applied but has no applied_at - cannot date the event honestly; set applied_at first',
              v_row.slug;
        END IF;

        INSERT INTO status_events (application_id, status, note, created_at)
        VALUES (v_row.id, 'applied', 'sent (was resume_drafted)', v_row.applied_at);

        RAISE NOTICE 'backfilled: % -> applied @ %', v_row.slug, v_row.applied_at;
        v_fixed := v_fixed + 1;
    END LOOP;

    IF v_fixed = 0 THEN
        RAISE NOTICE 'nothing to repair - every applied seat already has its status event';
    ELSE
        RAISE NOTICE 'OK - % status event(s) backfilled', v_fixed;
    END IF;
END $$;

-- Assert the invariant this file exists to restore: no applied seat without its event.
DO $$
DECLARE v_missing integer;
BEGIN
    SELECT count(*) INTO v_missing
      FROM applications a
     WHERE a.status = 'applied'
       AND NOT EXISTS (SELECT 1 FROM status_events e
                        WHERE e.application_id = a.id AND e.status = 'applied');
    IF v_missing > 0 THEN
        RAISE EXCEPTION 'still % applied seat(s) with no status event', v_missing;
    END IF;
    RAISE NOTICE 'verified - every applied seat has an applied status event';
END $$;

COMMIT;
