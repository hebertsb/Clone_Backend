-- Combined SQL inserts
SET session_replication_role = 'replica';

-- BEGIN FILE: contenttypes_ContentType.sql
-- SQL inserts for model: contenttypes.ContentType (table: django_content_type)
BEGIN;
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (1, 'admin', 'logentry');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (2, 'auth', 'permission');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (3, 'auth', 'group');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (5, 'sessions', 'session');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (6, 'authz', 'rol');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (7, 'authz', 'usuario');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (8, 'catalogo', 'categoria');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (9, 'catalogo', 'destino');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (10, 'catalogo', 'itinerario');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (11, 'catalogo', 'paquete');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (12, 'catalogo', 'servicio');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (13, 'reservas', 'acompanante');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (14, 'reservas', 'reserva');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (15, 'reservas', 'reservaacompanante');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (16, 'reservas', 'reservaservicio');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (17, 'cupones', 'cupon');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (18, 'descuentos', 'descuento');
INSERT INTO "django_content_type" ("id", "app_label", "model") VALUES (19, 'descuentos', 'serviciodescuento');
SELECT setval(pg_get_serial_sequence('django_content_type','id'), 19, true);
COMMIT;


-- BEGIN FILE: auth_Permission.sql
-- SQL inserts for model: auth.Permission (table: auth_permission)
BEGIN;
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (21, 'Can add rol', 6, 'add_rol');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (22, 'Can change rol', 6, 'change_rol');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (23, 'Can delete rol', 6, 'delete_rol');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (24, 'Can view rol', 6, 'view_rol');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (25, 'Can add usuario', 7, 'add_usuario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (26, 'Can change usuario', 7, 'change_usuario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (27, 'Can delete usuario', 7, 'delete_usuario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (28, 'Can view usuario', 7, 'view_usuario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (29, 'Can add categoria', 8, 'add_categoria');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (30, 'Can change categoria', 8, 'change_categoria');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (31, 'Can delete categoria', 8, 'delete_categoria');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (32, 'Can view categoria', 8, 'view_categoria');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (33, 'Can add destino', 9, 'add_destino');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (34, 'Can change destino', 9, 'change_destino');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (35, 'Can delete destino', 9, 'delete_destino');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (36, 'Can view destino', 9, 'view_destino');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (37, 'Can add itinerario', 10, 'add_itinerario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (38, 'Can change itinerario', 10, 'change_itinerario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (39, 'Can delete itinerario', 10, 'delete_itinerario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (40, 'Can view itinerario', 10, 'view_itinerario');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (41, 'Can add paquete', 11, 'add_paquete');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (42, 'Can change paquete', 11, 'change_paquete');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (43, 'Can delete paquete', 11, 'delete_paquete');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (44, 'Can view paquete', 11, 'view_paquete');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (45, 'Can add servicio', 12, 'add_servicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (46, 'Can change servicio', 12, 'change_servicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (47, 'Can delete servicio', 12, 'delete_servicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (48, 'Can view servicio', 12, 'view_servicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (65, 'Can add cupon', 17, 'add_cupon');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (66, 'Can change cupon', 17, 'change_cupon');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (67, 'Can delete cupon', 17, 'delete_cupon');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (68, 'Can view cupon', 17, 'view_cupon');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (69, 'Can add descuento', 18, 'add_descuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (70, 'Can change descuento', 18, 'change_descuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (71, 'Can delete descuento', 18, 'delete_descuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (72, 'Can view descuento', 18, 'view_descuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (73, 'Can add servicio descuento', 19, 'add_serviciodescuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (74, 'Can change servicio descuento', 19, 'change_serviciodescuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (75, 'Can delete servicio descuento', 19, 'delete_serviciodescuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (76, 'Can view servicio descuento', 19, 'view_serviciodescuento');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (49, 'Can add acompanante', 13, 'add_acompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (50, 'Can change acompanante', 13, 'change_acompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (51, 'Can delete acompanante', 13, 'delete_acompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (52, 'Can view acompanante', 13, 'view_acompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (53, 'Can add reserva', 14, 'add_reserva');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (54, 'Can change reserva', 14, 'change_reserva');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (55, 'Can delete reserva', 14, 'delete_reserva');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (56, 'Can view reserva', 14, 'view_reserva');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (57, 'Can add reserva acompanante', 15, 'add_reservaacompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (58, 'Can change reserva acompanante', 15, 'change_reservaacompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (59, 'Can delete reserva acompanante', 15, 'delete_reservaacompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (60, 'Can view reserva acompanante', 15, 'view_reservaacompanante');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (61, 'Can add reserva servicio', 16, 'add_reservaservicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (62, 'Can change reserva servicio', 16, 'change_reservaservicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (63, 'Can delete reserva servicio', 16, 'delete_reservaservicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (64, 'Can view reserva servicio', 16, 'view_reservaservicio');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (20, 'Can view session', 5, 'view_session');
SELECT setval(pg_get_serial_sequence('auth_permission','id'), 76, true);
COMMIT;


-- BEGIN FILE: auth_Group.sql
-- SQL inserts for model: auth.Group (table: auth_group)
BEGIN;
SELECT setval(pg_get_serial_sequence('auth_group','id'), 1, true);
COMMIT;


-- BEGIN FILE: authz_Rol.sql
-- SQL inserts for model: authz.Rol (table: authz_rol)
BEGIN;
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (1, 'ADMIN', '2025-09-15T15:32:32.494944+00:00', '2025-09-15T15:32:32.494944+00:00');
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (2, 'OPERADOR', '2025-09-15T15:32:33.816345+00:00', '2025-09-15T15:32:33.816345+00:00');
INSERT INTO "authz_rol" ("id", "nombre", "created_at", "updated_at") VALUES (3, 'CLIENTE', '2025-09-15T15:32:35.117284+00:00', '2025-09-15T15:32:35.117284+00:00');
SELECT setval(pg_get_serial_sequence('authz_rol','id'), 3, true);
COMMIT;


-- BEGIN FILE: authz_Usuario.sql
-- SQL inserts for model: authz.Usuario (table: authz_usuario)
BEGIN;
INSERT INTO "authz_usuario" ("id", "password", "last_login", "is_superuser", "nombres", "apellidos", "email", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais", "estado", "is_active", "is_staff", "date_joined") VALUES (1, 'pbkdf2_sha256$1000000$oerO2VSQ6YZPHaQrctxWWb$ZPDBZkCpv3Srr4R7Iw5SE0PlIF17fT7o1eRhza4vLJs=', NULL, false, 'hebert', 'suarez burgos', 'suarezburgoshebert@gmail.com', NULL, NULL, NULL, NULL, NULL, 'ACTIVO', true, false, '2025-09-15T15:31:49.220204+00:00');
INSERT INTO "authz_usuario" ("id", "password", "last_login", "is_superuser", "nombres", "apellidos", "email", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais", "estado", "is_active", "is_staff", "date_joined") VALUES (2, 'pbkdf2_sha256$1000000$g2vzemsKt1mtR8SuRbhUed$FkU+UoLrQ1HNKOx83gSezQC2asCcQQACxXUu5ITtf98=', NULL, false, 'Gabriel', 'Moreno', 'gabriel.moreno@autonoma.edu.bo', '70000001', NULL, NULL, NULL, NULL, 'ACTIVO', true, false, '2025-09-15T15:32:31.424619+00:00');
INSERT INTO "authz_usuario" ("id", "password", "last_login", "is_superuser", "nombres", "apellidos", "email", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais", "estado", "is_active", "is_staff", "date_joined") VALUES (3, 'pbkdf2_sha256$1000000$jRpfdqNXSmqzN2YNKfpUDR$wt4EyvO3KdSqUV4iTyi3CkP2g8TUL6xC4baPjPHUQtU=', NULL, false, 'María', 'Fernández', 'maria.fernandez@autonoma.edu.bo', '70000002', NULL, NULL, NULL, NULL, 'ACTIVO', true, false, '2025-09-15T15:32:32.772412+00:00');
INSERT INTO "authz_usuario" ("id", "password", "last_login", "is_superuser", "nombres", "apellidos", "email", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais", "estado", "is_active", "is_staff", "date_joined") VALUES (4, 'pbkdf2_sha256$1000000$BTEBvNVN9PhDTwLTZp8hfO$wUPHG4+y2whAb1ooWXeif9oZeBoCgzaEe4urJ/8lu/4=', NULL, false, 'Juan', 'Pérez', 'juan.perez@autonoma.edu.bo', '70000003', NULL, NULL, NULL, NULL, 'ACTIVO', true, false, '2025-09-15T15:32:34.083345+00:00');
INSERT INTO "authz_usuario_roles" ("usuario_id","rol_id") VALUES (2, 1);
INSERT INTO "authz_usuario_roles" ("usuario_id","rol_id") VALUES (3, 2);
INSERT INTO "authz_usuario_roles" ("usuario_id","rol_id") VALUES (4, 3);
SELECT setval(pg_get_serial_sequence('authz_usuario','id'), 4, true);
COMMIT;


-- BEGIN FILE: catalogo_Categoria.sql
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


-- BEGIN FILE: catalogo_Destino.sql
-- SQL inserts for model: catalogo.Destino (table: catalogo_destino)
BEGIN;
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (1, '2025-09-15T15:30:24.254198+00:00', '2025-09-15T15:30:24.254198+00:00', 'La Paz', 3, 'Ciudad capital con vistas espectaculares');
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (2, '2025-09-15T15:30:24.408213+00:00', '2025-09-15T15:30:24.408213+00:00', 'Santa Cruz', 4, 'Región tropical con naturaleza exuberante');
INSERT INTO "catalogo_destino" ("id", "created_at", "updated_at", "nombre", "dias", "descripcion") VALUES (3, '2025-09-15T15:30:24.562605+00:00', '2025-09-15T15:30:24.562605+00:00', 'Sucre', 2, 'Ciudad histórica y cultural');
SELECT setval(pg_get_serial_sequence('catalogo_destino','id'), 3, true);
COMMIT;


-- BEGIN FILE: catalogo_Itinerario.sql
-- SQL inserts for model: catalogo.Itinerario (table: catalogo_itinerario)
BEGIN;
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (1, '2025-09-15T15:30:24.708150+00:00', '2025-09-15T15:30:24.708150+00:00', 1, 'Llegada y tour por la ciudad', '["Recepción en aeropuerto", "Tour por la ciudad", "Cena privada con chef"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (2, '2025-09-15T15:30:24.884696+00:00', '2025-09-15T15:30:24.884696+00:00', 2, 'Aventura extrema', '["Bungee jumping", "Escalada en roca", "Caminata en la selva"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (3, '2025-09-15T15:30:25.041131+00:00', '2025-09-15T15:30:25.041131+00:00', 3, 'Relax y bienestar', '["Retiros de yoga", "Masajes terapéuticos", "Tour gastronómico local"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (4, '2025-09-15T15:30:25.231096+00:00', '2025-09-15T15:30:25.231096+00:00', 1, 'Exploración cultural', '["Visita a museos de arte", "Espectáculo de danza folklórica", "Clase de cocina regional"]');
INSERT INTO "catalogo_itinerario" ("id", "created_at", "updated_at", "dia", "titulo", "actividades") VALUES (5, '2025-09-15T15:30:25.364003+00:00', '2025-09-15T15:30:25.364003+00:00', 2, 'Ecoturismo', '["Avistamiento de aves", "Ecoturismo", "Rafting en río"]');
SELECT setval(pg_get_serial_sequence('catalogo_itinerario','id'), 5, true);
COMMIT;


-- BEGIN FILE: catalogo_Servicio.sql
-- SQL inserts for model: catalogo.Servicio (table: catalogo_servicio)
BEGIN;
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (1, 'Tour por la ciudad', 'Recorrido guiado por los principales puntos turísticos.', 'TOUR', 100.00, 1, true, '2025-09-15T15:12:58.402026+00:00', '2025-09-15T15:12:58.402026+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (2, 'Tour de aventura', 'Experiencia extrema en la naturaleza con actividades de rafting.', 'TOUR', 150.00, 1, true, '2025-09-15T15:12:58.568593+00:00', '2025-09-15T15:12:58.568593+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (3, 'Hotel 5 estrellas', 'Hospedaje de lujo con vista panorámica al mar.', 'ALOJAMIENTO', 250.00, 2, true, '2025-09-15T15:12:58.713523+00:00', '2025-09-15T15:12:58.713523+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (4, 'Cabaña en la montaña', 'Escapada a la naturaleza con alojamiento rústico.', 'ALOJAMIENTO', 80.00, 2, true, '2025-09-15T15:12:58.857973+00:00', '2025-09-15T15:12:58.857973+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (5, 'Transporte privado al aeropuerto', 'Servicio de transporte privado desde y hacia el aeropuerto.', 'TRANSPORTE', 50.00, 3, true, '2025-09-15T15:12:58.990975+00:00', '2025-09-15T15:12:58.990975+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (6, 'Tour en autobús turístico', 'Recorrido en autobús por los puntos turísticos más importantes de la ciudad.', 'TRANSPORTE', 30.00, 3, true, '2025-09-15T15:12:59.124146+00:00', '2025-09-15T15:12:59.124146+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (7, 'Caminata en la selva', 'Excursión guiada por la jungla, explorando flora y fauna local.', 'ACTIVIDAD', 60.00, 4, true, '2025-09-15T15:12:59.268363+00:00', '2025-09-15T15:12:59.268363+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (8, 'Bungee jumping', 'Aventura extrema saltando desde un puente.', 'ACTIVIDAD', 100.00, 4, true, '2025-09-15T15:12:59.391326+00:00', '2025-09-15T15:12:59.391326+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (9, 'Tour gastronómico local', 'Visita a restaurantes locales para degustar la comida típica.', 'EXPERIENCIA GASTRONÓMICA', 40.00, 5, true, '2025-09-15T15:12:59.524825+00:00', '2025-09-15T15:12:59.524825+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (10, 'Clase de cocina regional', 'Aprende a cocinar platos típicos de la región en un taller práctico.', 'EXPERIENCIA GASTRONÓMICA', 60.00, 5, true, '2025-09-15T15:12:59.668701+00:00', '2025-09-15T15:12:59.668701+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (11, 'Retiros de yoga', 'Retiro de bienestar para practicar yoga y meditación.', 'BIENESTAR', 150.00, 6, true, '2025-09-15T15:12:59.791364+00:00', '2025-09-15T15:12:59.791364+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (12, 'Masajes terapéuticos', 'Masajes relajantes y terapéuticos para aliviar tensiones.', 'BIENESTAR', 50.00, 6, true, '2025-09-15T15:12:59.924677+00:00', '2025-09-15T15:12:59.924677+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (13, 'Visita a museos de arte', 'Tour guiado por los museos más importantes de la ciudad.', 'CULTURAL', 20.00, 7, true, '2025-09-15T15:13:00.057882+00:00', '2025-09-15T15:13:00.057882+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (14, 'Espectáculo de danza folklórica', 'Disfruta de una representación de danza folklórica tradicional.', 'CULTURAL', 35.00, 7, true, '2025-09-15T15:13:00.191377+00:00', '2025-09-15T15:13:00.191377+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (15, 'Avistamiento de aves', 'Excursión para observar las aves en su hábitat natural.', 'ECOLOGICO', 70.00, 8, true, '2025-09-15T15:13:00.325448+00:00', '2025-09-15T15:13:00.325448+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (16, 'Ecoturismo', 'Excursión a parques naturales para promover el ecoturismo.', 'ECOLOGICO', 90.00, 8, true, '2025-09-15T15:13:00.468307+00:00', '2025-09-15T15:13:00.469315+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (17, 'Crucero de lujo', 'Experiencia de lujo en un crucero por la costa.', 'DE LUJO', 500.00, 9, true, '2025-09-15T15:13:00.602751+00:00', '2025-09-15T15:13:00.602751+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (18, 'Cena privada con chef', 'Cena exclusiva preparada por un chef en un lugar único.', 'DE LUJO', 200.00, 9, true, '2025-09-15T15:13:00.746423+00:00', '2025-09-15T15:13:00.746423+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (19, 'Escalada en roca', 'Aventura extrema escalando las rocas más desafiantes.', 'DE AVENTURA', 120.00, 10, true, '2025-09-15T15:13:00.890484+00:00', '2025-09-15T15:13:00.890484+00:00');
INSERT INTO "catalogo_servicio" ("id", "titulo", "descripcion", "tipo", "costo", "categoria_id", "visible_publico", "created_at", "updated_at") VALUES (20, 'Rafting en río', 'Desciende por un río salvaje en una emocionante experiencia de rafting.', 'DE AVENTURA', 90.00, 10, true, '2025-09-15T15:13:01.024469+00:00', '2025-09-15T15:13:01.024469+00:00');
SELECT setval(pg_get_serial_sequence('catalogo_servicio','id'), 20, true);
COMMIT;


-- BEGIN FILE: catalogo_Paquete.sql
-- SQL inserts for model: catalogo.Paquete (table: catalogo_paquete)
BEGIN;
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (1, '2025-09-15T15:30:25.690424+00:00', '2025-09-15T15:30:26.273785+00:00', 'Paquete Aventura Extrema La Paz', 'La Paz, Bolivia', 'Aventura extrema en la ciudad más alta del mundo', 'Experimenta la adrenalina en La Paz con bungee jumping, escalada y caminatas en la selva.', 4.5, 120, '450', '500', '3 días', 10, 'Alta', 14, '["https://example.com/image1.jpg", "https://example.com/image2.jpg"]', '["Tour por la ciudad", "Bungee jumping", "Escalada en roca", "Caminata en la selva", "Cena privada con chef"]', '["Vuelos internacionales", "Seguro de viaje"]', '["2023-10-01", "2023-10-15", "2023-11-01"]', 10.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (2, '2025-09-15T15:30:26.397980+00:00', '2025-09-15T15:30:26.784930+00:00', 'Paquete Relax Tropical Santa Cruz', 'Santa Cruz, Bolivia', 'Relajación en el trópico boliviano', 'Disfruta de retiros de yoga, masajes y experiencias gastronómicas en Santa Cruz.', 4.8, 85, '350', '400', '4 días', 8, 'Baja', 14, '["https://example.com/image3.jpg"]', '["Retiros de yoga", "Masajes terapéuticos", "Tour gastronómico local", "Hotel 5 estrellas"]', '["Transporte al aeropuerto", "Bebidas alcohólicas"]', '["2023-09-20", "2023-10-05"]', 5.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (3, '2025-09-15T15:30:26.898424+00:00', '2025-09-15T15:30:27.296401+00:00', 'Paquete Cultural Histórico Sucre', 'Sucre, Bolivia', 'Sumérgete en la historia y cultura de Sucre', 'Visita museos, disfruta de danzas folklóricas y aprende cocina regional en Sucre.', 4.7, 95, '250', '300', '2 días', 12, 'Media', 14, '["https://example.com/image4.jpg"]', '["Visita a museos de arte", "Espectáculo de danza folklórica", "Clase de cocina regional", "Transporte privado al aeropuerto"]', '["Almuerzos", "Souvenirs"]', '["2023-11-10", "2023-12-01"]', 15.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (4, '2025-09-15T15:30:27.420116+00:00', '2025-09-15T15:30:28.140803+00:00', 'Paquete Ecológico Aventura Combinado', 'La Paz y Santa Cruz, Bolivia', 'Ecoturismo y aventura en Bolivia', 'Combina avistamiento de aves, rafting y caminatas en un viaje inolvidable.', 4.6, 70, '550', '600', '5 días', 6, 'Media-Alta', 10, '["https://example.com/image5.jpg"]', '["Avistamiento de aves", "Ecoturismo", "Rafting en río", "Caminata en la selva", "Tour en autobús turístico"]', '["Equipo personal", "Propinas"]', '["2023-10-20", "2023-11-15"]', 8.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (5, '2025-09-15T15:30:28.265704+00:00', '2025-09-15T15:30:28.685526+00:00', 'Paquete de Lujo Ejecutivo', 'La Paz, Bolivia', 'Experiencia de lujo en La Paz', 'Disfruta de cruceros de lujo, cenas privadas y transporte exclusivo.', 5.0, 50, '1200', '1300', '3 días', 4, 'Baja', 9, '["https://example.com/image6.jpg"]', '["Crucero de lujo", "Cena privada con chef", "Transporte privado al aeropuerto", "Hotel 5 estrellas"]', '["Actividades opcionales", "Bebidas premium"]', '["2023-12-01", "2024-01-15"]', 20.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (6, '2025-09-15T15:30:28.809230+00:00', '2025-09-15T15:30:29.362956+00:00', 'Paquete Aventura Familiar Titicaca', 'La Paz / Titicaca, Bolivia', 'Excursión familiar al lago Titicaca', 'Navega por el Lago Titicaca, visita islas tradicionales y disfruta de actividades para toda la familia.', 4.4, 40, '380', '420', '3 días', 12, 'Baja', 14, '["https://example.com/titicaca1.jpg"]', '["Transporte terrestre", "Navegación en barco", "Alojamiento", "Guía local"]', '["Comidas especiales", "Gastos personales"]', '["2025-10-10", "2025-11-01"]', 7.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (7, '2025-09-15T15:30:29.486966+00:00', '2025-09-15T15:30:30.030398+00:00', 'Paquete Aventura Selvática', 'Santa Cruz, Bolivia', 'Explora la selva y su biodiversidad', 'Safari de un día y caminatas guiadas por la selva con alojamiento ecológico.', 4.5, 28, '420', '480', '4 días', 10, 'Media', 14, '["https://example.com/selva1.jpg"]', '["Traslados", "Guía naturalista", "Alojamiento ecológico"]', '["Vuelos", "Seguro"]', '["2025-10-20", "2025-11-10"]', 10.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (8, '2025-09-15T15:30:30.154779+00:00', '2025-09-15T15:30:30.618652+00:00', 'Paquete Gastronómico Sucre', 'Sucre, Bolivia', 'Experiencia culinaria regional', 'Tours gastronómicos, clases de cocina y visitas a mercados locales.', 4.9, 18, '300', '350', '2 días', 8, 'Baja', 14, '["https://example.com/gastronomia1.jpg"]', '["Clases de cocina", "Degustaciones", "Alojamiento"]', '["Bebidas alcohólicas"]', '["2025-09-25", "2025-10-15"]', 5.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (9, '2025-09-15T15:30:30.743657+00:00', '2025-09-15T15:30:31.473864+00:00', 'Paquete Trekking Andes', 'La Paz, Bolivia', 'Trekking de nivel medio en los Andes', 'Rutas guiadas por montañas, campamento y experiencias culturales en comunidades andinas.', 4.3, 22, '520', '590', '5 días', 12, 'Media-Alta', 14, '["https://example.com/andes1.jpg"]', '["Guía de montaña", "Equipo básico", "Alojamiento en refugios"]', '["Seguro de altura", "Comidas extras"]', '["2025-10-01", "2025-11-01"]', 12.00);
INSERT INTO "catalogo_paquete" ("id", "created_at", "updated_at", "nombre", "ubicacion", "descripcion_corta", "descripcion_completa", "calificacion", "numero_reseñas", "precio", "precio_original", "duracion", "max_personas", "dificultad", "categoria_id", "imagenes", "incluido", "no_incluido", "fechas_disponibles", "descuento") VALUES (10, '2025-09-15T15:30:31.610390+00:00', '2025-09-15T15:30:32.030723+00:00', 'Paquete Escapada Urbana 48h', 'La Paz, Bolivia', 'Fin de semana urbano con actividades premium', 'Experiencias gastronómicas, tours privados y alojamiento boutique para un fin de semana inolvidable.', 4.2, 12, '220', '260', '2 días', 6, 'Baja', 9, '["https://example.com/urban1.jpg"]', '["Tour privado", "Cena de bienvenida", "Alojamiento boutique"]', '["Traslados al aeropuerto"]', '["2025-09-20", "2025-10-10"]', 6.00);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (1, 1);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (2, 2);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (3, 3);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (4, 1);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (4, 2);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (5, 1);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (6, 1);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (7, 2);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (8, 3);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (9, 1);
INSERT INTO "catalogo_paquete_destinos" ("paquete_id","destino_id") VALUES (10, 1);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (1, 1);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (1, 2);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (2, 3);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (3, 4);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (4, 2);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (4, 5);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (5, 1);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (6, 1);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (6, 5);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (7, 2);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (7, 5);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (8, 4);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (9, 2);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (9, 3);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (9, 5);
INSERT INTO "catalogo_paquete_itinerario" ("paquete_id","itinerario_id") VALUES (10, 1);
SELECT setval(pg_get_serial_sequence('catalogo_paquete','id'), 10, true);
COMMIT;


-- BEGIN FILE: descuentos_Descuento.sql
-- SQL inserts for model: descuentos.Descuento (table: descuentos_descuento)
BEGIN;
INSERT INTO "descuentos_descuento" ("id", "created_at", "updated_at", "codigo", "tipo", "valor", "fecha_inicio", "fecha_fin", "estado") VALUES (1, '2025-09-15T15:31:28.069929+00:00', '2025-09-15T15:31:28.069929+00:00', 'DSC10', 'PORCENTAJE', 10.00, NULL, NULL, true);
INSERT INTO "descuentos_descuento" ("id", "created_at", "updated_at", "codigo", "tipo", "valor", "fecha_inicio", "fecha_fin", "estado") VALUES (2, '2025-09-15T15:31:28.233373+00:00', '2025-09-15T15:31:28.233373+00:00', 'MENOS5', 'FIJO', 5.00, NULL, NULL, true);
SELECT setval(pg_get_serial_sequence('descuentos_descuento','id'), 2, true);
COMMIT;


-- BEGIN FILE: descuentos_ServicioDescuento.sql
-- SQL inserts for model: descuentos.ServicioDescuento (table: descuentos_servicio_descuento)
BEGIN;
INSERT INTO "descuentos_servicio_descuento" ("id", "created_at", "updated_at", "servicio_id", "descuento_id", "prioridad", "exclusivo", "estado") VALUES (1, '2025-09-15T15:31:28.373522+00:00', '2025-09-15T15:31:28.373522+00:00', 1, 1, 1, true, true);
INSERT INTO "descuentos_servicio_descuento" ("id", "created_at", "updated_at", "servicio_id", "descuento_id", "prioridad", "exclusivo", "estado") VALUES (2, '2025-09-15T15:31:28.523238+00:00', '2025-09-15T15:31:28.523238+00:00', 1, 2, 2, false, true);
SELECT setval(pg_get_serial_sequence('descuentos_servicio_descuento','id'), 2, true);
COMMIT;


-- BEGIN FILE: cupones_Cupon.sql
-- SQL inserts for model: cupones.Cupon (table: cupones_cupon)
BEGIN;
SELECT setval(pg_get_serial_sequence('cupones_cupon','id'), 1, true);
COMMIT;


-- BEGIN FILE: reservas_Reserva.sql
-- SQL inserts for model: reservas.Reserva (table: reservas_reserva)
BEGIN;
INSERT INTO "reservas_reserva" ("id", "created_at", "updated_at", "usuario_id", "fecha_inicio", "estado", "cupon_id", "total", "moneda") VALUES (1, '2025-09-15T15:31:50.171486+00:00', '2025-09-15T15:31:50.171486+00:00', 1, '2025-09-15T13:00:00+00:00', 'PENDIENTE', NULL, 300.00, 'BOB');
SELECT setval(pg_get_serial_sequence('reservas_reserva','id'), 1, true);
COMMIT;


-- BEGIN FILE: reservas_ReservaServicio.sql
-- SQL inserts for model: reservas.ReservaServicio (table: reservas_reservaservicio)
BEGIN;
INSERT INTO "reservas_reservaservicio" ("id", "reserva_id", "servicio_id", "cantidad", "precio_unitario", "fecha_servicio") VALUES (1, 1, 1, 2, 100.00, '2025-09-15T13:00:00+00:00');
INSERT INTO "reservas_reservaservicio" ("id", "reserva_id", "servicio_id", "cantidad", "precio_unitario", "fecha_servicio") VALUES (2, 1, 2, 1, 100.00, '2025-09-16T13:00:00+00:00');
SELECT setval(pg_get_serial_sequence('reservas_reservaservicio','id'), 2, true);
COMMIT;


-- BEGIN FILE: reservas_Acompanante.sql
-- SQL inserts for model: reservas.Acompanante (table: reservas_visitante)
BEGIN;
INSERT INTO "reservas_visitante" ("id", "created_at", "updated_at", "documento", "nombre", "apellido", "fecha_nacimiento", "nacionalidad", "email", "telefono") VALUES (1, '2025-09-15T15:31:50.592146+00:00', '2025-09-15T15:31:50.592146+00:00', '12730324', 'Hebert', 'Suarez', '1999-08-01', 'Bolivia', 'suarezburgoshebert@gmail.com', '+591 731449637');
SELECT setval(pg_get_serial_sequence('reservas_visitante','id'), 1, true);
COMMIT;


-- BEGIN FILE: reservas_ReservaAcompanante.sql
-- SQL inserts for model: reservas.ReservaAcompanante (table: reservas_reservavisitante)
BEGIN;
INSERT INTO "reservas_reservavisitante" ("id", "reserva_id", "visitante_id", "estado", "es_titular") VALUES (1, 1, 1, 'CONFIRMADO', true);
SELECT setval(pg_get_serial_sequence('reservas_reservavisitante','id'), 1, true);
COMMIT;


-- BEGIN FILE: admin_LogEntry.sql
-- SQL inserts for model: admin.LogEntry (table: django_admin_log)
BEGIN;
SELECT setval(pg_get_serial_sequence('django_admin_log','id'), 1, true);
COMMIT;


-- BEGIN FILE: sessions_Session.sql
-- SQL inserts for model: sessions.Session (table: django_session)
BEGIN;
COMMIT;


SET session_replication_role = 'origin';
