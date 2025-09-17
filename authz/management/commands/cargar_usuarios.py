import json
from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol

class Command(BaseCommand):
    help = 'Carga usuarios iniciales desde initial_users.json'

    def handle(self, *args, **kwargs):
        with open('authz/fixtures/datos_usuarios.json', encoding='utf-8') as f:
            usuarios = json.load(f)
        for u in usuarios:
            fields = u.get('fields', {})
            if not fields or 'email' not in fields:
                continue  # Salta si no hay datos válidos
            usuario, creado = Usuario.objects.get_or_create(
                email=fields['email'],
                defaults={
                    'nombres': fields.get('nombres', ''),
                    'apellidos': fields.get('apellidos', ''),
                    'telefono': fields.get('telefono', ''),
                    'fecha_nacimiento': fields.get('fecha_nacimiento'),
                    'genero': fields.get('genero'),
                    'documento_identidad': fields.get('documento_identidad'),
                    'pais': fields.get('pais'),
                    'estado': fields.get('estado', 'ACTIVO'),
                }
            )
            if creado:
                usuario.set_password(fields.get('password', 'changeme'))
                usuario.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {usuario.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuario ya existe: {usuario.email}"))
            for nombre_rol in fields.get('roles', []):
                rol, _ = Rol.objects.get_or_create(nombre=nombre_rol)
                usuario.roles.add(rol)
        self.stdout.write(self.style.SUCCESS('Carga de usuarios completada.'))
