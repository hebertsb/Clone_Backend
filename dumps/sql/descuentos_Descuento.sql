-- SQL inserts for model: descuentos.Descuento (table: descuentos_descuento)
BEGIN;
INSERT INTO "descuentos_descuento" ("id", "created_at", "updated_at", "codigo", "tipo", "valor", "fecha_inicio", "fecha_fin", "estado") VALUES (1, '2025-09-15T15:31:28.069929+00:00', '2025-09-15T15:31:28.069929+00:00', 'DSC10', 'PORCENTAJE', 10.00, NULL, NULL, true);
INSERT INTO "descuentos_descuento" ("id", "created_at", "updated_at", "codigo", "tipo", "valor", "fecha_inicio", "fecha_fin", "estado") VALUES (2, '2025-09-15T15:31:28.233373+00:00', '2025-09-15T15:31:28.233373+00:00', 'MENOS5', 'FIJO', 5.00, NULL, NULL, true);
SELECT setval(pg_get_serial_sequence('descuentos_descuento','id'), 2, true);
COMMIT;
