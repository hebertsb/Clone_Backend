import os
import sys
import django
import json
from pathlib import Path

# Añadir la raíz del proyecto al sys.path
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from descuentos.models import Descuento, ServicioDescuento
from catalogo.models import Servicio, Categoria

JSON_PATH = BASE / 'descuentos' / 'descuentos.json'

if not JSON_PATH.exists():
    print('No existe', JSON_PATH)
    raise SystemExit(1)

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

descuentos = data.get('descuentos', [])
servicios_descuentos = data.get('servicios_descuentos', [])

for d in descuentos:
    codigo = d.get('codigo')
    tipo = d.get('tipo')
    valor = d.get('valor')
    estado = d.get('estado', True)
    if not codigo:
        continue
    try:
        valor_dec = float(valor)
    except Exception:
        valor_dec = 0.0
    obj, created = Descuento.objects.get_or_create(codigo=codigo, defaults={'tipo': tipo, 'valor': valor_dec, 'estado': estado})
    if created:
        print('Creado descuento:', codigo)
    else:
        print('Ya existe descuento:', codigo)

for sd in servicios_descuentos:
    servicio_info = sd.get('servicio') or {}
    descuento_codigo = sd.get('descuento')
    prioridad = sd.get('prioridad', 10)
    exclusivo = sd.get('exclusivo', True)
    estado = sd.get('estado', True)

    # localizar servicio por título y categoría si se indica
    servicio_qs = Servicio.objects.all()
    titulo = servicio_info.get('titulo')
    cat_nombre = servicio_info.get('categoria')
    if titulo:
        servicio_qs = servicio_qs.filter(titulo=titulo)
    if cat_nombre:
        servicio_qs = servicio_qs.filter(categoria__nombre=cat_nombre)
    servicio = servicio_qs.first()
    if not servicio:
        print('No se encontró servicio para', servicio_info)
        continue

    try:
        descuento = Descuento.objects.get(codigo=descuento_codigo)
    except Descuento.DoesNotExist:
        print('No existe descuento con codigo', descuento_codigo)
        continue

    obj, created = ServicioDescuento.objects.get_or_create(servicio=servicio, descuento=descuento,
                                                          defaults={'prioridad': prioridad, 'exclusivo': exclusivo, 'estado': estado})
    if created:
        print('Creada relación descuento->servicio:', servicio.titulo, '->', descuento.codigo)
    else:
        print('Ya existe relación:', servicio.titulo, '->', descuento.codigo)

print('Carga de descuentos completada.')
