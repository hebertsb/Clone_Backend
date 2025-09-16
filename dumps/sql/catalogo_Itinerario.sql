-- SQL inserts for model: catalogo.Itinerario (table: catalogo_itinerario)
BEGIN;
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (1, '2025-09-15T15:30:24.708150+00:00', '2025-09-15T15:30:24.708150+00:00', 1, 'Llegada y tour por la ciudad', '["Recepción en aeropuerto", "Tour por la ciudad", "Cena privada con chef"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (2, '2025-09-15T15:30:24.884696+00:00', '2025-09-15T15:30:24.884696+00:00', 2, 'Aventura extrema', '["Bungee jumping", "Escalada en roca", "Caminata en la selva"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (3, '2025-09-15T15:30:25.041131+00:00', '2025-09-15T15:30:25.041131+00:00', 3, 'Relax y bienestar', '["Retiros de yoga", "Masajes terapéuticos", "Tour gastronómico local"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (4, '2025-09-15T15:30:25.231096+00:00', '2025-09-15T15:30:25.231096+00:00', 1, 'Exploración cultural', '["Visita a museos de arte", "Espectáculo de danza folklórica", "Clase de cocina regional"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (5, '2025-09-15T15:30:25.364003+00:00', '2025-09-15T15:30:25.364003+00:00', 2, 'Ecoturismo', '["Avistamiento de aves", "Ecoturismo", "Rafting en río"]');
SELECT setval(pg_get_serial_sequence('catalogo_itinerario','id'), 5, true);
COMMIT;
