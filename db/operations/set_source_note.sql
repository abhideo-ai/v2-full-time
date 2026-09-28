-- db/operations/set_source_note.sql
--
-- Set (or clear) the source note on one seat: where the seat came from, in words.
-- The sibling of set_source_url.sql, which keeps the URL column a URL.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 \
--        -c "select set_config('src.slug','<slug>',false), set_config('src.note','<note or empty>',false)" \
--        -f db/operations/set_source_note.sql
--
-- Why this exists: jobs_sync.register writes the note once and never overwrites it,
-- so a note that turns out to be wrong (who sent the application, and how) had no
-- sanctioned way to be corrected. For text with quotes, put the set_config select in
-- a scratch .sql file with dollar quoting and pass it with -f before this file.
--
-- Passing an empty note clears the field. The timeline (application_events) is where
-- the correction itself is recorded; this column only holds the current wording.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_slug text := current_setting('src.slug', true);
    v_note text := nullif(trim(current_setting('src.note', true)), '');
    v_id   integer;
BEGIN
    SELECT id INTO v_id FROM applications WHERE slug = v_slug;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'no application with slug %', v_slug;
    END IF;

    UPDATE applications SET source_note = v_note WHERE id = v_id;
    RAISE NOTICE 'OK - % source_note = %', v_slug, COALESCE(v_note, 'NULL');
END $$;

COMMIT;
