from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservas.models import Reserva
from reservas.notifications import NotificacionReprogramacion
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envía recordatorios automáticos para reservas reprogramadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-antes',
            type=int,
            default=1,
            help='Número de días antes de la reserva para enviar el recordatorio (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué recordatorios se enviarían sin enviarlos realmente'
        )

    def handle(self, *args, **options):
        dias_antes = options['dias_antes']
        dry_run = options['dry_run']
        
        # Calcular la fecha objetivo para los recordatorios
        fecha_objetivo = timezone.now().date() + timedelta(days=dias_antes)
        
        # Buscar reservas reprogramadas que necesiten recordatorio
        reservas_para_recordatorio = Reserva.objects.filter(
            fecha_inicio__date=fecha_objetivo,
            estado='REPROGRAMADA',
            numero_reprogramaciones__gte=1
        ).select_related('usuario')
        
        total_reservas = reservas_para_recordatorio.count()
        
        if total_reservas == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'No hay reservas reprogramadas para recordatorio en {dias_antes} días.'
                )
            )
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'Encontradas {total_reservas} reservas reprogramadas para recordatorio.'
            )
        )
        
        exitosos = 0
        fallidos = 0
        
        for reserva in reservas_para_recordatorio:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Recordatorio para reserva #{reserva.pk} - {reserva.usuario.email}'
                    )
                    exitosos += 1
                else:
                    # Enviar recordatorio
                    resultado = NotificacionReprogramacion.enviar_recordatorio_reprogramacion(
                        reserva, dias_antes
                    )
                    
                    if resultado:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Recordatorio enviado para reserva #{reserva.pk} - {reserva.usuario.email}'
                            )
                        )
                        exitosos += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error enviando recordatorio para reserva #{reserva.pk} - {reserva.usuario.email}'
                            )
                        )
                        fallidos += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error procesando reserva #{reserva.pk}: {str(e)}'
                    )
                )
                fallidos += 1
                logger.error(f'Error en recordatorio para reserva {reserva.pk}: {str(e)}')
        
        # Resumen final
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN] Se habrían enviado {exitosos} recordatorios.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Recordatorios enviados exitosamente: {exitosos}'
                )
            )
            if fallidos > 0:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Recordatorios fallidos: {fallidos}'
                    )
                )
            
            logger.info(f'Comando recordatorios completado: {exitosos} exitosos, {fallidos} fallidos')