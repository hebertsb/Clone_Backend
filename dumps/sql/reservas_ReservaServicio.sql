-- SQL inserts for model: reservas.ReservaServicio (table: reservas_reservaservicio)
BEGIN;
INSERT INTO "reservas_reservaservicio" ("id", "reserva_id", "servicio_id", "cantidad", "precio_unitario", "fecha_servicio") VALUES (1, 1, 1, 2, 100.00, '2025-09-15T13:00:00+00:00');
INSERT INTO "reservas_reservaservicio" ("id", "reserva_id", "servicio_id", "cantidad", "precio_unitario", "fecha_servicio") VALUES (2, 1, 2, 1, 100.00, '2025-09-16T13:00:00+00:00');
SELECT setval(pg_get_serial_sequence('reservas_reservaservicio','id'), 2, true);
COMMIT;
