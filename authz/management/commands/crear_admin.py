from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol
from rest_framework_simplejwt.tokens import RefreshToken


class Command(BaseCommand):
    help = 'Crea un usuario admin y le asigna rol ADMIN. Uso: python manage.py crear_admin --email admin@example.com --password secret --nombres Admin --apellidos User'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email del admin')
        parser.add_argument('--password', required=True, help='Password')
        parser.add_argument('--nombres', required=True, help='Nombres')
        parser.add_argument('--apellidos', required=True, help='Apellidos')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nombres = options['nombres']
        apellidos = options['apellidos']

        # crear roles si no existen
        admin_role, _ = Rol.objects.get_or_create(nombre='ADMIN')
        Rol.objects.get_or_create(nombre='OPERADOR')
        Rol.objects.get_or_create(nombre='CLIENTE')

        # crear usuario (si ya existe, actualizar contraseña y nombres)
        user, created = Usuario.objects.get_or_create(email=email, defaults={
            'nombres': nombres,
            'apellidos': apellidos,
            'is_staff': True,
            'estado': 'ACTIVO',
        })
        if not created:
            user.nombres = nombres
            user.apellidos = apellidos
            user.is_staff = True
            user.estado = 'ACTIVO'
        user.set_password(password)
        user.save()

        # asignar rol ADMIN
        user.roles.add(admin_role)

        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        self.stdout.write(self.style.SUCCESS(f'Usuario admin creado/actualizado: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Access token: {access}'))
