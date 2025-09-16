# Notas de migraciones y pasos realizados

Resumen corto
- Durante la puesta en marcha local se detectaron inconsistencias entre el historial de migraciones en el repositorio y el estado real de la base de datos `db.sqlite3`.
- Para resolverlo se tomaron medidas conservadoras: backup de `db.sqlite3` (`db.sqlite3.backup`), restauración de migraciones borradas desde `HEAD`, aplicación explícita de migraciones faltantes y, en casos donde la BD ya contenía los cambios, marcado de migraciones como aplicadas usando `--fake` o insertando entradas en la tabla `django_migrations`.

Comandos clave ejecutados localmente
- `python -m venv .venv` (creación de entorno virtual)
- `.venv\Scripts\pip.exe install -r requirements.txt` (instalación deps)
- `.venv\Scripts\python.exe manage.py migrate --noinput` (aplicar migraciones)
- `.venv\Scripts\python.exe manage.py migrate descuentos` (aplicación puntual)
- Inserciones puntuales en `django_migrations` o `manage.py migrate reservas 0003 --fake` cuando la BD ya contenía las tablas/columnas correspondientes.

Recomendaciones para colaboradores
- Al clonar el repositorio por primera vez, ejecutar el script de ayuda (opcionalmente con creación de venv e instalación):
  - PowerShell (Windows): `powershell -ExecutionPolicy Bypass -File .\scripts\setup_after_clone.ps1 -CreateVenv -InstallDeps -RunMigrations -LoadData`
  - Bash (Linux/macOS/Git Bash): `bash scripts/setup_after_clone.sh --venv --install --migrate --loaddata`

- Si encuentras errores de migraciones faltantes o tablas ausentes, evita borrar archivos de migración del repositorio. En su lugar, coordina con el equipo. Si la BD local ya contiene los cambios, usa `manage.py migrate <app> <migration> --fake` para marcar como aplicadas o pide instrucciones al autor de las migraciones.

Notas de auditoría
- Se creó un respaldo `db.sqlite3.backup` antes de cualquier cambio destructivo.
- Algunas migraciones locales fueron editadas temporalmente para resolver conflictos de `project_state`. Si el equipo prefiere, esas ediciones pueden revertirse y las migraciones re-aplicarse en una BD limpia.

Comando recomendado — sólo migraciones

Si sólo necesitas aplicar las migraciones (sin crear virtualenv ni instalar dependencias), usa el script mínimo incluido:

- PowerShell (Windows):

```powershell
powershell -File .\scripts\migrate_all.ps1
```

- Bash (Linux/macOS/Git Bash):

```bash
bash scripts/migrate_all.sh
```

Notas:
- Si en tu entorno local tienes un virtualenv llamado `.venv` en la raíz, los scripts preferirán usar `.venv` automáticamente; si no, usarán el `python` disponible en PATH.
- Ejecuta los scripts desde la raíz del repositorio.

Fin del documento.
# Notas de migraciones y pasos realizados

Resumen corto
- Durante la puesta en marcha local se detectaron inconsistencias entre el historial de migraciones en el repositorio y el estado real de la base de datos `db.sqlite3`.
- Para resolverlo se tomaron medidas conservadoras: backup de `db.sqlite3` (`db.sqlite3.backup`), restauración de migraciones borradas desde `HEAD`, aplicación explícita de migraciones faltantes y, en casos donde la BD ya contenía los cambios, marcado de migraciones como aplicadas usando `--fake` o insertando entradas en la tabla `django_migrations`.

Comandos clave ejecutados localmente
- `python -m venv .venv` (creación de entorno virtual)
- `.venv\Scripts\pip.exe install -r requirements.txt` (instalación deps)
- `.venv\Scripts\python.exe manage.py migrate --noinput` (aplicar migraciones)
- `.venv\Scripts\python.exe manage.py migrate descuentos` (aplicación puntual)
- Inserciones puntuales en `django_migrations` o `manage.py migrate reservas 0003 --fake` cuando la BD ya contenía las tablas/columnas correspondientes.

Recomendaciones para colaboradores
- Al clonar el repositorio por primera vez, ejecutar el script de ayuda:
  - PowerShell (Windows): `powershell -ExecutionPolicy Bypass -File .\scripts\setup_after_clone.ps1 -CreateVenv -InstallDeps -RunMigrations -LoadData`
  - Bash (Linux/macOS/Git Bash): `bash scripts/setup_after_clone.sh --venv --install --migrate --loaddata`

- Si encuentras errores de migraciones faltantes o tablas ausentes, evita borrar archivos de migración del repositorio. En su lugar, coordina con el equipo. Si la BD local ya contiene los cambios, usa `manage.py migrate <app> <migration> --fake` para marcar como aplicadas o pide instrucciones al autor de las migraciones.

Notas de auditoría
- Se creó un respaldo `db.sqlite3.backup` antes de cualquier cambio destructivo.
- Algunas migraciones locales fueron editadas temporalmente para resolver conflictos de `project_state`. Si el equipo prefiere, esas ediciones pueden revertirse y las migraciones re-aplicarse en una BD limpia.
