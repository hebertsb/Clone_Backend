import os
import sys
import django
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from catalogo.models import Destino, Itinerario, Categoria, Paquete

JSON_PATH = BASE / 'catalogo' / 'fixtures' / 'paquetes_sample.json'
if not JSON_PATH.exists():
    print('No existe', JSON_PATH)
    raise SystemExit(1)

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    objs = json.load(f)

# Procesar en orden, creando objetos con los PKs indicados cuando sea posible
for node in objs:
    model = node.get('model')
    pk = node.get('pk')
    fields = node.get('fields', {})

    if model == 'catalogo.destino':
        if Destino.objects.filter(pk=pk).exists():
            print('Destino ya existe pk', pk)
            continue
        Destino.objects.create(id=pk, nombre=fields.get('nombre', ''), dias=fields.get('dias', 0), descripcion=fields.get('descripcion', ''))
        print('Creado Destino pk', pk)

    elif model == 'catalogo.itinerario':
        if Itinerario.objects.filter(pk=pk).exists():
            print('Itinerario ya existe pk', pk)
            continue
        Itinerario.objects.create(id=pk, dia=fields.get('dia', 0), titulo=fields.get('titulo', ''), actividades=fields.get('actividades', []))
        print('Creado Itinerario pk', pk)

    elif model == 'catalogo.categoria':
        nombre = fields.get('nombre')
        if Categoria.objects.filter(pk=pk).exists() or Categoria.objects.filter(nombre=nombre).exists():
            print('Categoria ya existe pk/nombre', pk, nombre)
            continue
        Categoria.objects.create(id=pk, nombre=nombre)
        print('Creada Categoria pk', pk, 'nombre', nombre)

    elif model == 'catalogo.paquete':
        if Paquete.objects.filter(pk=pk).exists():
            print('Paquete ya existe pk', pk)
            continue
        # resolver categoria
        categoria_pk = fields.get('categoria')
        categoria = None
        if categoria_pk:
            categoria = Categoria.objects.filter(pk=categoria_pk).first()
        if not categoria:
            # fallback: buscar categoria llamada 'Paquetes' o crear una
            categoria, _ = Categoria.objects.get_or_create(nombre='Paquetes')
        # crear paquete
        paquete = Paquete.objects.create(
            id=pk,
            nombre=fields.get('nombre',''),
            ubicacion=fields.get('ubicacion',''),
            descripcion_corta=fields.get('descripcion_corta',''),
            descripcion_completa=fields.get('descripcion_completa',''),
            calificacion=fields.get('calificacion',0),
            numero_reseñas=fields.get('numero_reseñas',0),
            precio=str(fields.get('precio','')),
            precio_original=str(fields.get('precio_original','')),
            duracion=fields.get('duracion',''),
            max_personas=fields.get('max_personas',0),
            dificultad=fields.get('dificultad',''),
            categoria=categoria,
            imagenes=fields.get('imagenes', []),
            incluido=fields.get('incluido', []),
            no_incluido=fields.get('no_incluido', []),
            fechas_disponibles=fields.get('fechas_disponibles', []),
            descuento=fields.get('descuento')
        )
        # relaciones M2M: destinos e itinerario
        destinos_pks = fields.get('destinos', [])
        for dpk in destinos_pks:
            d = Destino.objects.filter(pk=dpk).first()
            if d:
                paquete.destinos.add(d)
            else:
                print('Destino faltante pk', dpk, 'para paquete', pk)
        itinerario_pks = fields.get('itinerario', [])
        for ipk in itinerario_pks:
            it = Itinerario.objects.filter(pk=ipk).first()
            if it:
                paquete.itinerario.add(it)
            else:
                print('Itinerario faltante pk', ipk, 'para paquete', pk)
        paquete.save()
        print('Creado Paquete pk', pk, 'nombre', paquete.nombre)

print('Carga de paquetes completada.')
