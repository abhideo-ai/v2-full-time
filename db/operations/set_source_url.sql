-- db/operations/set_source_url.sql
--
-- Set (or clear) the posting URL on one seat.
--
--   psql -d jobs_tracker_v2 -v ON_ERROR_STOP=1 \
--        -c "select set_config('src.slug','<slug>',false), set_config('src.url','<url or empty>',false)" \
--        -f db/operations/set_source_url.sql
--
-- Why this exists: source_url was being filled with PROSE ("naukri (listing URL not
-- captured)"), which the launcher renders as a broken link. The field is a URL or it
-- is NULL. When it is NULL the launcher says "no workspace, no posting URL", which is
-- honest; a prose value looks like a link and is not one.
--
-- Passing an empty url clears the field.

\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
    v_slug text := current_setting('src.slug', true);
    v_url  text := nullif(trim(current_setting('src.url', true)), '');
    v_id   integer;
BEGIN
    SELECT id INTO v_id FROM applications WHERE slug = v_slug;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'no application with slug %', v_slug;
    END IF;

    -- A URL or nothing. Prose in this column is the bug this file exists to stop.
    IF v_url IS NOT NULL AND v_url !~ '^https?://' THEN
        RAISE EXCEPTION 'source_url must start with http:// or https://, got %', v_url;
    END IF;

    UPDATE applications SET source_url = v_url WHERE id = v_id;
    RAISE NOTICE 'OK - % source_url = %', v_slug, COALESCE(v_url, 'NULL (no posting URL)');
END $$;

COMMIT;
