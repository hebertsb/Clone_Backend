from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Elimina el historial de migraciones de la app catalogo en la base de datos.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app='catalogo';")
        self.stdout.write(self.style.SUCCESS('Historial de migraciones de catalogo eliminado correctamente.'))
