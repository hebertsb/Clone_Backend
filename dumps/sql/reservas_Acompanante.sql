-- SQL inserts for model: reservas.Acompanante (table: reservas_visitante)
BEGIN;
INSERT INTO "reservas_visitante" ("id", "created_at", "updated_at", "documento", "nombre", "apellido", "fecha_nacimiento", "nacionalidad", "email", "telefono") VALUES (1, '2025-09-15T15:31:50.592146+00:00', '2025-09-15T15:31:50.592146+00:00', '12730324', 'Hebert', 'Suarez', '1999-08-01', 'Bolivia', 'suarezburgoshebert@gmail.com', '+591 731449637');
SELECT setval(pg_get_serial_sequence('reservas_visitante','id'), 1, true);
COMMIT;
