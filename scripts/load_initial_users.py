import os
import sys
import django
from pathlib import Path
import json

# Añadir la raíz del proyecto al sys.path para que `backend` sea importable
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authz.models import Usuario, Rol

JSON_PATH = BASE / 'authz' / 'initial_users.json'
if not JSON_PATH.exists():
    print('No existe', JSON_PATH)
    raise SystemExit(1)

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

for u in data:
    email = u.get('email')
    if not email:
        continue
    usuario, created = Usuario.objects.get_or_create(email=email, defaults={
        'nombres': u.get('nombres',''),
        'apellidos': u.get('apellidos',''),
        'telefono': u.get('telefono',''),
        'estado': u.get('estado','ACTIVO')
    })
    if created:
        usuario.set_password(u.get('password','changeme'))
        usuario.save()
        print('Usuario creado', email)
    else:
        print('Usuario ya existe', email)
    # asignar roles
    for rname in u.get('roles', []):
        rol, _ = Rol.objects.get_or_create(nombre=rname)
        usuario.roles.add(rol)
print('Carga de usuarios completada.')
