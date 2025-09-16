-- SQL inserts for model: authz.Rol (table: authz_rol)
BEGIN;
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (1, 'ADMIN', '2025-09-15T15:32:32.494944+00:00', '2025-09-15T15:32:32.494944+00:00');
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (2, 'OPERADOR', '2025-09-15T15:32:33.816345+00:00', '2025-09-15T15:32:33.816345+00:00');
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (3, 'CLIENTE', '2025-09-15T15:32:35.117284+00:00', '2025-09-15T15:32:35.117284+00:00');
SELECT setval(pg_get_serial_sequence('authz_rol','id'), 3, true);
COMMIT;
