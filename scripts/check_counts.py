import os
import django
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
django.setup()

from authz.models import Usuario
from catalogo.models import Servicio, Paquete
from reservas.models import Reserva, Acompanante
from descuentos.models import Descuento

print('Counts:')
print('Usuarios', Usuario.objects.count())
print('Servicios', Servicio.objects.count())
print('Paquetes', Paquete.objects.count())
print('Reservas', Reserva.objects.count())
print('Acompanantes', Acompanante.objects.count())
print('Descuentos', Descuento.objects.count())
