-- SQL inserts for model: admin.LogEntry (table: django_admin_log)
BEGIN;
SELECT setval(pg_get_serial_sequence('django_admin_log','id'), 1, true);
COMMIT;
