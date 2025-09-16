-- SQL inserts for model: cupones.Cupon (table: cupones_cupon)
BEGIN;
SELECT setval(pg_get_serial_sequence('cupones_cupon','id'), 1, true);
COMMIT;
