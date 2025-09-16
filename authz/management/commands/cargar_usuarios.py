import json
from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol

class Command(BaseCommand):
    help = 'Carga usuarios iniciales desde initial_users.json'

    def handle(self, *args, **kwargs):
        with open('authz/initial_users.json', encoding='utf-8') as f:
            usuarios = json.load(f)
        for u in usuarios:
            usuario, creado = Usuario.objects.get_or_create(
                email=u['email'],
                defaults={
                    'nombres': u['nombres'],
                    'apellidos': u['apellidos'],
                    'telefono': u.get('telefono', ''),
                    'fecha_nacimiento': u.get('fecha_nacimiento'),
                    'genero': u.get('genero'),
                    'documento_identidad': u.get('documento_identidad'),
                    'pais': u.get('pais'),
                    'estado': u.get('estado', 'ACTIVO'),
                }
            )
            if creado:
                usuario.set_password(u['password'])
                usuario.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {usuario.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuario ya existe: {usuario.email}"))
            # Asignar roles
            for nombre_rol in u.get('roles', []):
                rol, _ = Rol.objects.get_or_create(nombre=nombre_rol)
                usuario.roles.add(rol)
        self.stdout.write(self.style.SUCCESS('Carga de usuarios completada.'))
