-- SQL inserts for model: reservas.ReservaAcompanante (table: reservas_reservavisitante)
BEGIN;
INSERT INTO "reservas_reservavisitante" ("id", "reserva_id", "visitante_id", "estado", "es_titular") VALUES (1, 1, 1, 'CONFIRMADO', true);
SELECT setval(pg_get_serial_sequence('reservas_reservavisitante','id'), 1, true);
COMMIT;
