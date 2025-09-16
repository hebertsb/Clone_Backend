-- SQL inserts for model: reservas.Reserva (table: reservas_reserva)
BEGIN;
INSERT INTO "reservas_reserva" ("id", "created_at", "updated_at", "usuario_id", "fecha_inicio", "estado", "cupon_id", "total", "moneda") VALUES (1, '2025-09-15T15:31:50.171486+00:00', '2025-09-15T15:31:50.171486+00:00', 1, '2025-09-15T13:00:00+00:00', 'PENDIENTE', NULL, 300.00, 'BOB');
SELECT setval(pg_get_serial_sequence('reservas_reserva','id'), 1, true);
COMMIT;
