from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone

from reservas.models import Reserva, ReservaServicio, Acompanante
from catalogo.models import Servicio, Categoria
from authz.models import Usuario


class ReservaUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create admin user (model uses nombres/apellidos/email)
        self.user = Usuario.objects.create(nombres='Admin', apellidos='User', email='admin@example.com')
        self.user.set_password('pass')
        self.user.save()
        # give ADMIN role
        from authz.models import Rol
        admin_role, _ = Rol.objects.get_or_create(nombre='ADMIN')
        self.user.roles.add(admin_role)
        # authenticate client as this user
        self.client.force_authenticate(user=self.user)
        # create required categoria and servicio
        cat = Categoria.objects.create(nombre='Cat')
        self.servicio = Servicio.objects.create(titulo='Serv', tipo='GEN', categoria=cat, costo=100)
        # create reserva (provide required total and moneda)
        self.reserva = Reserva.objects.create(usuario=self.user, fecha_inicio=timezone.now(), total=0, moneda='BOB')
        ReservaServicio.objects.create(reserva=self.reserva, servicio=self.servicio, cantidad=1, precio_unitario=self.servicio.costo)

    def test_patch_with_incomplete_acompanante_returns_400(self):
        url = reverse('reserva-detail', args=[self.reserva.pk])
        payload = {
            "acompanantes": [
                {"nombre": "Juan", "apellido": "Perez"}  # missing fecha_nacimiento
            ]
        }
        response = self.client.patch(url, payload, format='json')
        # DRF Response objects have status_code
        self.assertEqual(getattr(response, 'status_code', None), 400)
        # response.data may be a dict-like
        self.assertIn('acompanantes', getattr(response, 'data', {}))

    def test_patch_with_complete_acompanante_creates_it(self):
        # create acompanante first and then associate by id
        acomp = Acompanante.objects.create(nombre='Ana', apellido='Lopez', fecha_nacimiento='1990-01-01')
        url = reverse('reserva-detail', args=[self.reserva.pk])
        payload = {
            "acompanantes": [
                {"acompanante_id": getattr(acomp, 'pk', None)}
            ]
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(getattr(response, 'status_code', None), 200)
        # verify association
        self.reserva.refresh_from_db()
        # Access related manager safely
        acomp_count = getattr(self.reserva, 'acompanantes').count() if hasattr(self.reserva, 'acompanantes') else 0
        self.assertEqual(acomp_count, 1)
        payload = {
            'acompanantes': [
                {'acompanante_id': getattr(acomp, 'pk', None)}
            ]
        }
        resp = self.client.patch(url, payload, format='json')
        if getattr(resp, 'status_code', None) not in (200, 204):
            self.fail(f"Unexpected status {getattr(resp, 'status_code', resp)}: {getattr(resp, 'data', getattr(resp, 'content', None))}")
        # verificar que la asociación se creó
        exists = False
        acomp_manager = getattr(self.reserva, 'acompanantes', None)
        if acomp_manager is not None:
            exists = acomp_manager.filter(acompanante__id=getattr(acomp, 'pk', None)).exists()
        self.assertTrue(exists)
