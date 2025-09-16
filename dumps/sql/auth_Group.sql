-- SQL inserts for model: auth.Group (table: auth_group)
BEGIN;
SELECT setval(pg_get_serial_sequence('auth_group','id'), 1, true);
COMMIT;
