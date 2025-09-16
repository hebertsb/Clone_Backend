import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
import django
django.setup()

from django.db import connection
from catalogo.models import Categoria, Servicio, Destino, Paquete, Itinerario
from reservas.models import Reserva, ReservaServicio, Acompanante, ReservaAcompanante
from cupones.models import Cupon
from descuentos.models import Descuento, ServicioDescuento
from authz.models import Usuario, Rol

models = [
    ('catalogo.Categoria', Categoria),
    ('catalogo.Servicio', Servicio),
    ('catalogo.Destino', Destino),
    ('catalogo.Paquete', Paquete),
    ('catalogo.Itinerario', Itinerario),
    ('reservas.Reserva', Reserva),
    ('reservas.ReservaServicio', ReservaServicio),
    ('reservas.Acompanante', Acompanante),
    ('reservas.ReservaAcompanante', ReservaAcompanante),
    ('cupones.Cupon', Cupon),
    ('descuentos.Descuento', Descuento),
    ('descuentos.ServicioDescuento', ServicioDescuento),
    ('authz.Usuario', Usuario),
    ('authz.Rol', Rol),
]

print('Usando archivo DB:', connection.settings_dict.get('NAME'))
for name, M in models:
    try:
        print(f"{name}: {M.objects.count()}")
    except Exception as e:
        print(f"{name}: ERROR ->", e)
        
