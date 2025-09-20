# soporte/management/commands/setup_soporte.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from soporte.models import ConfiguracionSoporte
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    """
    Comando para configurar el sistema de soporte por primera vez.
    
    Uso:
    python manage.py setup_soporte
    """
    
    help = 'Configura el sistema de soporte: grupos, configuración inicial y usuarios de ejemplo'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='No crear usuarios de ejemplo',
        )
        
        parser.add_argument(
            '--reset-config',
            action='store_true',
            help='Resetear configuración existente',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Configurando Sistema de Soporte ===')
        )
        
        try:
            with transaction.atomic():
                # 1. Crear grupos necesarios
                self.crear_grupos()
                
                # 2. Configurar sistema
                self.configurar_sistema(options['reset_config'])
                
                # 3. Crear usuarios de ejemplo (opcional)
                if not options['skip_users']:
                    self.crear_usuarios_ejemplo()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Sistema de soporte configurado correctamente')
                )
                self.mostrar_resumen()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error configurando sistema: {str(e)}')
            )
            raise
    
    def crear_grupos(self):
        """Crear grupos necesarios para el sistema de soporte."""
        self.stdout.write('📋 Creando grupos necesarios...')
        
        # Grupo para agentes de soporte
        soporte_group, created = Group.objects.get_or_create(name='Soporte')
        if created:
            self.stdout.write(f'  ✅ Grupo "Soporte" creado')
        else:
            self.stdout.write(f'  ℹ️  Grupo "Soporte" ya existe')
        
        # Grupo para administradores (opcional)
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write(f'  ✅ Grupo "Administradores" creado')
        else:
            self.stdout.write(f'  ℹ️  Grupo "Administradores" ya existe')
    
    def configurar_sistema(self, reset=False):
        """Configurar el sistema de soporte."""
        self.stdout.write('⚙️  Configurando sistema de soporte...')
        
        if reset and ConfiguracionSoporte.objects.exists():
            ConfiguracionSoporte.objects.all().delete()
            self.stdout.write('  🔄 Configuración existente eliminada')
        
        if not ConfiguracionSoporte.objects.exists():
            config = ConfiguracionSoporte.objects.create(
                # Tiempos SLA por defecto (en horas)
                tiempo_respuesta_critica=1,      # 1 hora
                tiempo_respuesta_alta=4,         # 4 horas  
                tiempo_respuesta_media=8,        # 8 horas
                tiempo_respuesta_baja=24,        # 24 horas
                
                # Configuración de asignación y notificaciones
                asignacion_automatica=True,
                max_solicitudes_por_agente=10,
                enviar_emails_cliente=True,
                enviar_emails_soporte=False,
                
                # Configuración de cierre automático
                dias_auto_cierre_resueltas=7,
                recordatorio_cliente_dias=3
            )
            self.stdout.write('  ✅ Configuración inicial creada')
            self.stdout.write(f'     - SLA Crítica: {config.tiempo_respuesta_critica}h')
            self.stdout.write(f'     - SLA Alta: {config.tiempo_respuesta_alta}h')
            self.stdout.write(f'     - SLA Media: {config.tiempo_respuesta_media}h')
            self.stdout.write(f'     - SLA Baja: {config.tiempo_respuesta_baja}h')
            self.stdout.write(f'     - Auto-asignación: {"Habilitada" if config.asignacion_automatica else "Deshabilitada"}')
            self.stdout.write(f'     - Max solicitudes por agente: {config.max_solicitudes_por_agente}')
        else:
            self.stdout.write('  ℹ️  Configuración ya existe (usar --reset-config para reiniciar)')
    
    def crear_usuarios_ejemplo(self):
        """Crear usuarios de ejemplo para testing."""
        self.stdout.write('👥 Creando usuarios de ejemplo...')
        
        # Crear agente de soporte de ejemplo
        if not User.objects.filter(email='agente@empresa.com').exists():
            agente = User.objects.create(
                email='agente@empresa.com',
                nombres='Agente',
                apellidos='de Soporte',
                is_staff=True,
                estado='ACTIVO'
            )
            agente.set_password('soporte123')
            agente.save()
            
            # Agregar al grupo de soporte
            soporte_group = Group.objects.get(name='Soporte')
            agente.groups.add(soporte_group)
            
            self.stdout.write('  ✅ Usuario agente de soporte creado')
            self.stdout.write('     Email: agente@empresa.com')
            self.stdout.write('     Password: soporte123')
        else:
            self.stdout.write('  ℹ️  Usuario agente ya existe')
        
        # Crear cliente de ejemplo
        if not User.objects.filter(email='cliente@test.com').exists():
            cliente = User.objects.create(
                email='cliente@test.com',
                nombres='Cliente',
                apellidos='de Prueba',
                estado='ACTIVO'
            )
            cliente.set_password('cliente123')
            cliente.save()
            
            self.stdout.write('  ✅ Usuario cliente de prueba creado')
            self.stdout.write('     Email: cliente@test.com')
            self.stdout.write('     Password: cliente123')
        else:
            self.stdout.write('  ℹ️  Usuario cliente ya existe')
        
        # Crear administrador de ejemplo
        if not User.objects.filter(email='admin@empresa.com').exists():
            admin = User.objects.create(
                email='admin@empresa.com',
                nombres='Administrador',
                apellidos='de Soporte',
                is_staff=True,
                is_superuser=True,
                estado='ACTIVO'
            )
            admin.set_password('admin123')
            admin.save()
            
            # Agregar a ambos grupos
            soporte_group = Group.objects.get(name='Soporte')
            admin_group = Group.objects.get(name='Administradores')
            admin.groups.add(soporte_group, admin_group)
            
            self.stdout.write('  ✅ Usuario administrador creado')
            self.stdout.write('     Email: admin@empresa.com')
            self.stdout.write('     Password: admin123')
        else:
            self.stdout.write('  ℹ️  Usuario admin ya existe')
    
    def mostrar_resumen(self):
        """Mostrar resumen de la configuración."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE CONFIGURACIÓN'))
        self.stdout.write('='*50)
        
        # Contar elementos
        total_users = User.objects.count()
        agentes_soporte = User.objects.filter(groups__name='Soporte').count()
        config = ConfiguracionSoporte.objects.first()
        
        self.stdout.write(f'👥 Total usuarios: {total_users}')
        self.stdout.write(f'🛠️  Agentes de soporte: {agentes_soporte}')
        self.stdout.write(f'⚙️  Configuración: {"Configurada" if config else "No configurada"}')
        
        if config:
            self.stdout.write(f'📧 Email clientes: {"Habilitado" if config.enviar_emails_cliente else "Deshabilitado"}')
            self.stdout.write(f'🔄 Auto-asignación: {"Habilitada" if config.asignacion_automatica else "Deshabilitada"}')
        
        self.stdout.write('\n📚 PRÓXIMOS PASOS:')
        self.stdout.write('1. Ejecutar migraciones: python manage.py migrate')
        self.stdout.write('2. Instalar dependencias: pip install drf-nested-routers django-filter')
        self.stdout.write('3. Probar API en: /api/soporte/solicitudes/')
        self.stdout.write('4. Acceder al admin en: /admin/')
        self.stdout.write('5. Configurar email en settings.py si es necesario')
        
        self.stdout.write('\n🔗 ENDPOINTS PRINCIPALES:')
        self.stdout.write('- GET  /api/soporte/solicitudes/          (listar solicitudes)')
        self.stdout.write('- POST /api/soporte/solicitudes/          (crear solicitud)')
        self.stdout.write('- GET  /api/soporte/dashboard/            (dashboard soporte)')
        self.stdout.write('- GET  /api/soporte/mis-estadisticas/     (estadísticas cliente)')
        
        self.stdout.write('\n' + '='*50)