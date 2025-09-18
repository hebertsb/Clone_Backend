from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Ejecuta makemigrations, migrate y carga fixtures automáticamente'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('→ Ejecutando makemigrations...'))
        call_command('makemigrations')

        self.stdout.write(self.style.NOTICE('→ Ejecutando migrate...'))
        call_command('migrate')

        self.stdout.write(self.style.NOTICE('→ Cargando fixtures...'))
        fixtures = [
            'roles_seed.json',
            'datos_usuarios.json',
            'categoria.json',
            'servicio.json',
            'paquete.json',
            'itinerario.json',
            'datos_cupones.json',
            'datos_descuentos.json',
            'datos_reserva.json'
        ]

        for fixture in fixtures:
            try:
                call_command('loaddata', fixture)
                self.stdout.write(self.style.SUCCESS(f'✔ Fixture cargado: {fixture}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ Error al cargar {fixture}: {e}'))
