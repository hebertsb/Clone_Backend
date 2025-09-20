"""
Comando de gestión para configurar reglas de reprogramación iniciales.
Este comando crea un conjunto básico de reglas que pueden ser personalizadas después.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from reservas.models import ReglasReprogramacion, ConfiguracionGlobalReprogramacion


class Command(BaseCommand):
    help = 'Configura reglas de reprogramación iniciales para el sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todas las reglas existentes antes de crear las nuevas',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué reglas se crearían sin ejecutar la acción',
        )
        parser.add_argument(
            '--perfil',
            type=str,
            choices=['basico', 'estricto', 'flexible'],
            default='basico',
            help='Perfil de reglas a aplicar (basico, estricto, flexible)',
        )
    
    def handle(self, *args, **options):
        perfil = options['perfil']
        dry_run = options['dry_run']
        reset = options['reset']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Mostrando qué se haría sin ejecutar')
            )
        
        try:
            with transaction.atomic():
                if reset:
                    self._reset_reglas(dry_run)
                
                self._crear_reglas_por_perfil(perfil, dry_run)
                self._crear_configuraciones_globales(dry_run)
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS('Configuración mostrada exitosamente (DRY-RUN)')
                    )
                    # Hacer rollback en dry-run
                    transaction.set_rollback(True)
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Reglas del perfil "{perfil}" configuradas exitosamente')
                    )
        
        except Exception as e:
            raise CommandError(f'Error configurando reglas: {str(e)}')
    
    def _reset_reglas(self, dry_run):
        """Elimina todas las reglas existentes."""
        if dry_run:
            count_reglas = ReglasReprogramacion.objects.count()
            count_configs = ConfiguracionGlobalReprogramacion.objects.count()
            self.stdout.write(
                f'Se eliminarían {count_reglas} reglas y {count_configs} configuraciones'
            )
        else:
            count_reglas = ReglasReprogramacion.objects.count()
            count_configs = ConfiguracionGlobalReprogramacion.objects.count()
            
            ReglasReprogramacion.objects.all().delete()
            ConfiguracionGlobalReprogramacion.objects.all().delete()
            
            self.stdout.write(
                f'Eliminadas {count_reglas} reglas y {count_configs} configuraciones existentes'
            )
    
    def _crear_reglas_por_perfil(self, perfil, dry_run):
        """Crea reglas según el perfil seleccionado."""
        reglas_data = self._obtener_reglas_perfil(perfil)
        
        if dry_run:
            self.stdout.write(f'\\nReglas del perfil "{perfil}" que se crearían:')
            for regla in reglas_data:
                self.stdout.write(f'  - {regla["nombre"]}: {regla["tipo_regla"]} ({regla["aplicable_a"]})')
        else:
            for regla_data in reglas_data:
                regla, created = ReglasReprogramacion.objects.get_or_create(
                    tipo_regla=regla_data['tipo_regla'],
                    aplicable_a=regla_data['aplicable_a'],
                    defaults=regla_data
                )
                
                if created:
                    self.stdout.write(f'✓ Creada: {regla.nombre}')
                else:
                    self.stdout.write(f'⚠ Ya existe: {regla.nombre}')
    
    def _crear_configuraciones_globales(self, dry_run):
        """Crea configuraciones globales básicas."""
        configs_data = [
            {
                'clave': 'EMAIL_NOTIFICACIONES',
                'valor': 'true',
                'descripcion': 'Habilitar envío de notificaciones por email',
                'tipo_valor': 'BOOLEAN'
            },
            {
                'clave': 'ADMIN_EMAILS',
                'valor': 'admin@tuagencia.com',
                'descripcion': 'Emails de administradores para notificaciones',
                'tipo_valor': 'LISTA'
            },
            {
                'clave': 'RECORDATORIOS_ACTIVOS',
                'valor': 'true',
                'descripcion': 'Activar recordatorios automáticos de reprogramaciones',
                'tipo_valor': 'BOOLEAN'
            },
            {
                'clave': 'DIAS_RECORDATORIO',
                'valor': '1',
                'descripcion': 'Días antes de la reserva para enviar recordatorio',
                'tipo_valor': 'INTEGER'
            },
            {
                'clave': 'LOG_REPROGRAMACIONES',
                'valor': 'true',
                'descripcion': 'Registrar logs detallados de reprogramaciones',
                'tipo_valor': 'BOOLEAN'
            }
        ]
        
        if dry_run:
            self.stdout.write('\\nConfiguraciones globales que se crearían:')
            for config in configs_data:
                self.stdout.write(f'  - {config["clave"]}: {config["valor"]}')
        else:
            for config_data in configs_data:
                config, created = ConfiguracionGlobalReprogramacion.objects.get_or_create(
                    clave=config_data['clave'],
                    defaults=config_data
                )
                
                if created:
                    self.stdout.write(f'✓ Configuración creada: {config.clave}')
                else:
                    self.stdout.write(f'⚠ Configuración ya existe: {config.clave}')
    
    def _obtener_reglas_perfil(self, perfil):
        """Obtiene las reglas según el perfil seleccionado."""
        
        reglas_basicas = [
            # Tiempo mínimo estándar para todos
            {
                'nombre': 'Tiempo mínimo estándar',
                'tipo_regla': 'TIEMPO_MINIMO',
                'aplicable_a': 'ALL',
                'valor_numerico': 24,
                'prioridad': 1,
                'mensaje_error': 'Debe reprogramar con al menos 24 horas de anticipación.',
                'activa': True
            },
            # Límite de reprogramaciones para clientes
            {
                'nombre': 'Límite reprogramaciones clientes',
                'tipo_regla': 'LIMITE_REPROGRAMACIONES',
                'aplicable_a': 'CLIENTE',
                'valor_numerico': 3,
                'prioridad': 1,
                'mensaje_error': 'Ha alcanzado el límite máximo de 3 reprogramaciones por reserva.',
                'activa': True
            },
            # Restricción días domingo
            {
                'nombre': 'Sin reprogramaciones domingos',
                'tipo_regla': 'DIAS_BLACKOUT',
                'aplicable_a': 'ALL',
                'valor_texto': '["domingo"]',
                'prioridad': 2,
                'mensaje_error': 'No se permite reprogramar para días domingo.',
                'activa': True
            }
        ]
        
        if perfil == 'basico':
            return reglas_basicas
        
        elif perfil == 'estricto':
            reglas_estrictas = reglas_basicas + [
                # Tiempo mínimo más estricto para clientes
                {
                    'nombre': 'Tiempo mínimo clientes estricto',
                    'tipo_regla': 'TIEMPO_MINIMO',
                    'aplicable_a': 'CLIENTE',
                    'valor_numerico': 48,
                    'prioridad': 1,
                    'mensaje_error': 'Los clientes deben reprogramar con al menos 48 horas de anticipación.',
                    'activa': True
                },
                # Límite diario de reprogramaciones
                {
                    'nombre': 'Límite diario reprogramaciones',
                    'tipo_regla': 'LIMITE_DIARIO',
                    'aplicable_a': 'CLIENTE',
                    'valor_numerico': 2,
                    'prioridad': 1,
                    'mensaje_error': 'No puede hacer más de 2 reprogramaciones por día.',
                    'activa': True
                },
                # Penalización por reprogramar
                {
                    'nombre': 'Penalización reprogramación',
                    'tipo_regla': 'DESCUENTO_PENALIZACION',
                    'aplicable_a': 'CLIENTE',
                    'valor_decimal': 5.0,
                    'prioridad': 1,
                    'mensaje_error': 'Se aplicará una penalización del 5% por reprogramar.',
                    'activa': True
                },
                # Horas blackout nocturnas
                {
                    'nombre': 'Sin reprogramaciones nocturnas',
                    'tipo_regla': 'HORAS_BLACKOUT',
                    'aplicable_a': 'ALL',
                    'valor_texto': '[22, 23, 0, 1, 2, 3, 4, 5]',
                    'prioridad': 2,
                    'mensaje_error': 'No se permite reprogramar entre las 22:00 y 06:00 horas.',
                    'activa': True
                }
            ]
            return reglas_estrictas
        
        elif perfil == 'flexible':
            reglas_flexibles = [
                # Tiempo mínimo reducido para todos
                {
                    'nombre': 'Tiempo mínimo flexible',
                    'tipo_regla': 'TIEMPO_MINIMO',
                    'aplicable_a': 'ALL',
                    'valor_numerico': 12,
                    'prioridad': 1,
                    'mensaje_error': 'Debe reprogramar con al menos 12 horas de anticipación.',
                    'activa': True
                },
                # Sin límite para administradores
                {
                    'nombre': 'Sin límite admins',
                    'tipo_regla': 'LIMITE_REPROGRAMACIONES',
                    'aplicable_a': 'ADMIN',
                    'valor_numerico': 999,
                    'prioridad': 1,
                    'mensaje_error': 'Los administradores no tienen límite de reprogramaciones.',
                    'activa': True
                },
                # Límite alto para clientes
                {
                    'nombre': 'Límite alto clientes',
                    'tipo_regla': 'LIMITE_REPROGRAMACIONES',
                    'aplicable_a': 'CLIENTE',
                    'valor_numerico': 5,
                    'prioridad': 2,
                    'mensaje_error': 'Ha alcanzado el límite de 5 reprogramaciones por reserva.',
                    'activa': True
                },
                # Tiempo mínimo muy reducido para admins
                {
                    'nombre': 'Tiempo mínimo admins',
                    'tipo_regla': 'TIEMPO_MINIMO',
                    'aplicable_a': 'ADMIN',
                    'valor_numerico': 2,
                    'prioridad': 1,
                    'mensaje_error': 'Los administradores pueden reprogramar con 2 horas de anticipación.',
                    'activa': True
                }
            ]
            return reglas_flexibles
        
        return reglas_basicas