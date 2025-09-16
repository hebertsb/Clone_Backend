import os
import sys
import django
import json
from pathlib import Path

# Añadir la raíz del proyecto al sys.path para poder importar `backend`
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

# Ajustar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from catalogo.models import Categoria, Servicio

JSON_PATH = BASE / 'catalogo' / 'initial_data.json'

if not JSON_PATH.exists():
    print('No existe', JSON_PATH)
    raise SystemExit(1)

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

categorias = data.get('categorias', [])
servicios = data.get('servicios', [])

# Crear categorias
for c in categorias:
    nombre = c.get('nombre') or c.get('nombre')
    if not nombre:
        continue
    cat, created = Categoria.objects.get_or_create(nombre=nombre)
    if created:
        print('Creada categoria:', nombre)

# Crear servicios
created_count = 0
for s in servicios:
    titulo = s.get('titulo')
    if not titulo:
        continue
    try:
        categoria_pk = int(s.get('categoria')) if s.get('categoria') is not None else None
    except Exception:
        categoria_pk = None
    categoria = None
    if categoria_pk:
        try:
            categoria = Categoria.objects.get(pk=categoria_pk)
        except Categoria.DoesNotExist:
            # fallback: usar la primera categoria
            categoria = Categoria.objects.first()
    else:
        categoria = Categoria.objects.first()
    if not categoria:
        print('No hay categoria para servicio', titulo)
        continue
    defaults = {
        'descripcion': s.get('descripcion',''),
        'tipo': s.get('tipo') or s.get('tipo',''),
        'costo': s.get('costo') or 0,
        'visible_publico': bool(s.get('visible_publico', True)),
    }
    obj, created = Servicio.objects.get_or_create(titulo=titulo, categoria=categoria, defaults=defaults)
    if created:
        created_count += 1
        print('Creado servicio:', titulo)

print('Total servicios creados:', created_count)
print('Total servicios en DB:', Servicio.objects.count())
