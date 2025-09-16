import os
import sys
import django
import json
from pathlib import Path
from decimal import Decimal

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from reservas.models import Reserva as ReservaModel, ReservaServicio as ReservaServicioModel, Acompanante as AcompananteModel, ReservaAcompanante as ReservaAcompananteModel
from authz.models import Usuario as UsuarioModel
from catalogo.models import Servicio as ServicioModel

JSON_PATH = BASE / 'scripts' / 'reserva_2.json'
if not JSON_PATH.exists():
    print('No existe', JSON_PATH)
    raise SystemExit(1)

with open(JSON_PATH, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Crear o obtener usuario (si el usuario viene con id que no existe, crear uno mínimo)
usuario_info = data.get('usuario') or {}
usuario = None
if usuario_info:
    email = usuario_info.get('email')
    if email:
        usuario = UsuarioModel.objects.filter(email=email).first()
    if not usuario:
        usuario = UsuarioModel.objects.create(
            nombres=usuario_info.get('nombres','Anonimo'),
            apellidos=usuario_info.get('apellidos',''),
            email=email or f'user_{usuario_info.get("id",0)}@example.com'
        )
        usuario.set_password('test1234')
        usuario.save()
        print('Usuario creado para reserva:', usuario.email)

# Crear reserva
reserva: ReservaModel = ReservaModel.objects.create(
    usuario=usuario,
    fecha_inicio=data.get('fecha_inicio'),
    estado=data.get('estado','PENDIENTE'),
    total=Decimal(str(data.get('total','0'))),
    moneda=data.get('moneda','BOB')
)
print('Reserva creada pk', reserva.pk)

# Crear detalles
for d in data.get('detalles', []):
    servicio_pk = d.get('servicio')
    servicio = None
    if servicio_pk:
        servicio = ServicioModel.objects.filter(pk=servicio_pk).first()
    else:
        # intentar por titulo
        titulo = d.get('titulo')
        if titulo:
            servicio = ServicioModel.objects.filter(titulo=titulo).first()
    if not servicio:
        print('No se encontró servicio para detalle', d)
        continue
    cantidad = d.get('cantidad',1)
    precio = Decimal(str(d.get('precio_unitario', '0')))
    fecha_servicio = d.get('fecha_servicio')
    rs: ReservaServicioModel = ReservaServicioModel.objects.create(reserva=reserva, servicio=servicio, cantidad=cantidad, precio_unitario=precio, fecha_servicio=fecha_servicio)
    print('Creado detalle para servicio', servicio.titulo)

# Crear acompañantes
for a in data.get('acompanantes', []):
    acom_info = a.get('acompanante') or {}
    documento = acom_info.get('documento')
    if documento:
        acompanante, created = AcompananteModel.objects.get_or_create(documento=documento, defaults={
            'nombre': acom_info.get('nombre',''),
            'apellido': acom_info.get('apellido',''),
            'fecha_nacimiento': acom_info.get('fecha_nacimiento'),
            'nacionalidad': acom_info.get('nacionalidad'),
            'email': acom_info.get('email'),
            'telefono': acom_info.get('telefono')
        })
    else:
        # usar conteo de ReservaAcompanante para evitar acceso dinámico a related-name
        count = ReservaAcompananteModel.objects.filter(reserva=reserva).count()
        acompanante = AcompananteModel.objects.create(
            documento=f'auto-{reserva.pk}-{count}',
            nombre=acom_info.get('nombre',''),
            apellido=acom_info.get('apellido',''),
            fecha_nacimiento=acom_info.get('fecha_nacimiento') or '2000-01-01'
        )
    es_titular = a.get('es_titular', False)
    estado = a.get('estado','CONFIRMADO')
    ReservaAcompananteModel.objects.create(reserva=reserva, acompanante=acompanante, estado=estado, es_titular=es_titular)
    print('Creado acompanante', acompanante.nombre)

print('Carga de reserva completada.')
