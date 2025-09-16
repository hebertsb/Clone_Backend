-- SQL inserts for model: catalogo.Destino (table: catalogo_destino)
BEGIN;
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (1, '2025-09-15T15:30:24.254198+00:00', '2025-09-15T15:30:24.254198+00:00', 'La Paz', 3, 'Ciudad capital con vistas espectaculares');
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (2, '2025-09-15T15:30:24.408213+00:00', '2025-09-15T15:30:24.408213+00:00', 'Santa Cruz', 4, 'Región tropical con naturaleza exuberante');
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (3, '2025-09-15T15:30:24.562605+00:00', '2025-09-15T15:30:24.562605+00:00', 'Sucre', 2, 'Ciudad histórica y cultural');
SELECT setval(pg_get_serial_sequence('catalogo_destino','id'), 3, true);
COMMIT;
