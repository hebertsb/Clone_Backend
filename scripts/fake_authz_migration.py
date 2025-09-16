from pathlib import Path
import sqlite3
from datetime import datetime
DB = Path('db.sqlite3')
if not DB.exists():
    print('No existe db.sqlite3 en el proyecto. Abortando.')
    raise SystemExit(1)
conn = sqlite3.connect(DB)
c = conn.cursor()
# Verificar existencia de tabla django_migrations
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
if not c.fetchone():
    print('No existe la tabla django_migrations. Abortando.')
    conn.close()
    raise SystemExit(1)
# Check if authz 0001 already present
c.execute("SELECT COUNT(*) FROM django_migrations WHERE app=? AND name=?", ('authz','0001_initial'))
if c.fetchone()[0] > 0:
    print('authz.0001_initial ya aparece en django_migrations')
else:
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    c.execute("INSERT INTO django_migrations(app, name, applied) VALUES (?,?,?)", ('authz','0001_initial', now))
    conn.commit()
    print('Insertada fila authz.0001_initial en django_migrations')
conn.close()
