-- SQL inserts for model: descuentos.ServicioDescuento (table: descuentos_servicio_descuento)
BEGIN;
INSERT INTO "descuentos_servicio_descuento" ("id", "created_at", "updated_at", "servicio_id", "descuento_id", "prioridad", "exclusivo", "estado") VALUES (1, '2025-09-15T15:31:28.373522+00:00', '2025-09-15T15:31:28.373522+00:00', 1, 1, 1, true, true);
INSERT INTO "descuentos_servicio_descuento" ("id", "created_at", "updated_at", "servicio_id", "descuento_id", "prioridad", "exclusivo", "estado") VALUES (2, '2025-09-15T15:31:28.523238+00:00', '2025-09-15T15:31:28.523238+00:00', 1, 2, 2, false, true);
SELECT setval(pg_get_serial_sequence('descuentos_servicio_descuento','id'), 2, true);
COMMIT;
