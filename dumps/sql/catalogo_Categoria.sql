-- SQL inserts for model: catalogo.Categoria (table: catalogo_categoria)
BEGIN;
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (1, 'Tours');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (2, 'Alojamiento');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (3, 'Transporte');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (4, 'Actividades');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (5, 'Experiencias Gastronómicas');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (6, 'Bienestar');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (7, 'Culturales');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (8, 'Ecológicos');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (9, 'De lujo');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (10, 'De aventura');
INSERT INTO "catalogo_categoria" ("id", "nombre") VALUES (14, 'Paquetes');
SELECT setval(pg_get_serial_sequence('catalogo_categoria','id'), 14, true);
COMMIT;
