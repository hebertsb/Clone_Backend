# soporte/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.utils import timezone

from .models import SolicitudSoporte, MensajeSoporte, ConfiguracionSoporte


@admin.register(ConfiguracionSoporte)
class ConfiguracionSoporteAdmin(admin.ModelAdmin):
    """
    Administración de la configuración del sistema de soporte.
    """
    
    list_display = [
        'pk',
        'tiempo_respuesta_critica',
        'tiempo_respuesta_alta', 
        'asignacion_automatica',
        'enviar_emails_cliente',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'asignacion_automatica',
        'enviar_emails_cliente',
        'enviar_emails_soporte',
        'created_at'
    ]
    
    search_fields = []
    
    fieldsets = (
        ('Tiempos de Respuesta (SLA)', {
            'fields': (
                'tiempo_respuesta_critica',
                'tiempo_respuesta_alta',
                'tiempo_respuesta_media',
                'tiempo_respuesta_baja'
            ),
            'description': 'Configure los tiempos máximos de respuesta según la prioridad'
        }),
        ('Configuración de Asignación', {
            'fields': (
                'asignacion_automatica',
                'max_solicitudes_por_agente'
            ),
            'description': 'Configuración para la asignación automática de solicitudes'
        }),
        ('Notificaciones', {
            'fields': (
                'enviar_emails_cliente',
                'enviar_emails_soporte'
            ),
            'description': 'Configuración de notificaciones por email'
        }),
        ('Cierre Automático', {
            'fields': (
                'dias_auto_cierre_resueltas',
                'recordatorio_cliente_dias'
            ),
            'description': 'Configuración de cierre automático y recordatorios'
        })
    )
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar la configuración principal."""
        return False
    
    def has_add_permission(self, request):
        """Solo permitir una configuración."""
        return not ConfiguracionSoporte.objects.exists()


class MensajeSoporteInline(admin.TabularInline):
    """
    Inline para mostrar mensajes dentro de las solicitudes.
    """
    
    model = MensajeSoporte
    extra = 0
    readonly_fields = ['created_at', 'leido_por_cliente', 'leido_por_soporte']
    fields = [
        'remitente',
        'contenido',
        'es_interno',
        'created_at',
        'leido_por_cliente',
        'leido_por_soporte'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('remitente')


@admin.register(SolicitudSoporte)
class SolicitudSoporteAdmin(admin.ModelAdmin):
    """
    Administración de solicitudes de soporte.
    """
    
    list_display = [
        'numero_ticket',
        'cliente_info',
        'asunto_truncated',
        'tipo_solicitud',
        'estado_colored',
        'prioridad_colored',
        'agente_soporte',
        'created_at',
        'fecha_limite_respuesta',
        'tiempo_transcurrido'
    ]
    
    list_filter = [
        'tipo_solicitud',
        'estado',
        'prioridad',
        'agente_soporte',
        'created_at',
        'fecha_limite_respuesta',
        'satisfaccion_cliente'
    ]
    
    search_fields = [
        'numero_ticket',
        'asunto',
        'descripcion',
        'cliente__username',
        'cliente__email',
        'cliente__first_name',
        'cliente__last_name'
    ]
    
    readonly_fields = [
        'numero_ticket',
        'created_at',
        'updated_at',
        'fecha_primera_respuesta',
        'fecha_resolucion'
    ]
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': (
                'numero_ticket',
                'cliente',
                'asunto',
                'descripcion',
                'reserva'
            )
        }),
        ('Clasificación', {
            'fields': (
                'tipo_solicitud',
                'prioridad',
                'estado'
            )
        }),
        ('Asignación y Gestión', {
            'fields': (
                'agente_soporte',
                'fecha_limite_respuesta',
                'notas_internas'
            )
        }),
        ('Métricas de Tiempo', {
            'fields': (
                'created_at',
                'updated_at',
                'fecha_primera_respuesta',
                'fecha_resolucion'
            ),
            'classes': ('collapse',)
        }),
        ('Satisfacción del Cliente', {
            'fields': (
                'satisfaccion_cliente',
                'comentarios_satisfaccion'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [MensajeSoporteInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente', 'agente_soporte', 'reserva'
        ).prefetch_related('mensajes')
    
    def cliente_info(self, obj):
        """Mostrar información del cliente."""
        if obj.cliente:
            nombre = f"{obj.cliente.nombres} {obj.cliente.apellidos}"
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                nombre,
                obj.cliente.email
            )
        return '-'
    cliente_info.short_description = "Cliente"  # type: ignore
    
    def asunto_truncated(self, obj):
        """Mostrar asunto truncado."""
        if len(obj.asunto) > 50:
            return obj.asunto[:50] + '...'
        return obj.asunto
    asunto_truncated.short_description = "Asunto"  # type: ignore
    
    def estado_colored(self, obj):
        """Mostrar estado con colores."""
        colors = {
            'PENDIENTE': '#ff9800',  # Naranja
            'EN_PROCESO': '#2196f3',  # Azul
            'ESPERANDO_CLIENTE': '#ff5722',  # Rojo-naranja
            'RESUELTO': '#4caf50',  # Verde
            'CERRADO': '#9e9e9e',  # Gris
            'CANCELADO': '#f44336'  # Rojo
        }
        color = colors.get(obj.estado, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_colored.short_description = "Estado"  # type: ignore
    
    def prioridad_colored(self, obj):
        """Mostrar prioridad con colores."""
        colors = {
            'BAJA': '#4caf50',      # Verde
            'MEDIA': '#ff9800',     # Naranja
            'ALTA': '#ff5722',      # Rojo-naranja
            'CRITICA': '#f44336'    # Rojo
        }
        color = colors.get(obj.prioridad, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_colored.short_description = "Prioridad"  # type: ignore
    
    def tiempo_transcurrido(self, obj):
        """Mostrar tiempo transcurrido desde la creación."""
        if obj.estado in ['RESUELTO', 'CERRADO']:
            fecha_fin = obj.fecha_resolucion or obj.updated_at
            delta = fecha_fin - obj.created_at
        else:
            delta = timezone.now() - obj.created_at
        
        horas = delta.total_seconds() / 3600
        
        if horas < 24:
            return f"{horas:.1f} horas"
        else:
            dias = horas / 24
            return f"{dias:.1f} días"
    tiempo_transcurrido.short_description = "Tiempo transcurrido"  # type: ignore
    
    actions = ['asignar_agente_bulk', 'cambiar_estado_bulk']
    
    def asignar_agente_bulk(self, request, queryset):
        """Acción bulk para asignar agente."""
        # Obtener agentes de soporte disponibles
        from django.contrib.auth.models import Group
        agentes = Group.objects.get(name='Soporte').user_set.filter(is_active=True)
        
        if not agentes.exists():
            self.message_user(request, "No hay agentes de soporte disponibles", level='ERROR')
            return
        
        # Asignación round-robin simple
        solicitudes_actualizadas = 0
        for i, solicitud in enumerate(queryset.filter(agente_soporte__isnull=True)):
            agente = agentes[i % agentes.count()]
            solicitud.asignar_agente(agente)
            solicitudes_actualizadas += 1
        
        self.message_user(
            request, 
            f"Se asignaron {solicitudes_actualizadas} solicitudes a agentes disponibles"
        )
    asignar_agente_bulk.short_description = "Asignar agente automáticamente"  # type: ignore
    
    def cambiar_estado_bulk(self, request, queryset):
        """Acción bulk para cambiar estado."""
        # Esta acción requeriría un formulario intermedio
        # Por simplicidad, cambiaremos a EN_PROCESO las solicitudes PENDIENTES
        solicitudes_actualizadas = queryset.filter(estado='PENDIENTE').update(estado='EN_PROCESO')
        
        self.message_user(
            request,
            f"Se cambiaron {solicitudes_actualizadas} solicitudes a EN_PROCESO"
        )
    cambiar_estado_bulk.short_description = "Marcar como En Proceso"  # type: ignore


@admin.register(MensajeSoporte)
class MensajeSoporteAdmin(admin.ModelAdmin):
    """
    Administración de mensajes de soporte.
    """
    
    list_display = [
        'solicitud_info',
        'remitente',
        'contenido_truncated',
        'es_interno',
        'created_at',
        'estado_lectura'
    ]
    
    list_filter = [
        'es_interno',
        'leido_por_cliente',
        'leido_por_soporte',
        'created_at',
        'solicitud__tipo_solicitud',
        'solicitud__estado'
    ]
    
    search_fields = [
        'contenido',
        'solicitud__numero_ticket',
        'remitente__username',
        'remitente__email'
    ]
    
    readonly_fields = [
        'created_at',
        'fecha_lectura_cliente',
        'fecha_lectura_soporte'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'solicitud', 'remitente'
        )
    
    def solicitud_info(self, obj):
        """Mostrar información de la solicitud."""
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            reverse('admin:soporte_solicitudsoporte_change', args=[obj.solicitud.id]),
            obj.solicitud.numero_ticket,
            obj.solicitud.asunto[:30] + '...' if len(obj.solicitud.asunto) > 30 else obj.solicitud.asunto
        )
    solicitud_info.short_description = "Solicitud"  # type: ignore
    
    def contenido_truncated(self, obj):
        """Mostrar contenido truncado."""
        if len(obj.contenido) > 100:
            return obj.contenido[:100] + '...'
        return obj.contenido
    contenido_truncated.short_description = "Contenido"  # type: ignore
    
    def estado_lectura(self, obj):
        """Mostrar estado de lectura."""
        cliente_icon = "✓" if obj.leido_por_cliente else "✗"
        soporte_icon = "✓" if obj.leido_por_soporte else "✗"
        
        return format_html(
            'Cliente: {} | Soporte: {}',
            cliente_icon,
            soporte_icon
        )
    estado_lectura.short_description = "Leído por"  # type: ignore


# Configuración adicional del admin
admin.site.site_header = "Sistema de Soporte - Administración"
admin.site.site_title = "Soporte Admin"
admin.site.index_title = "Panel de Administración del Sistema de Soporte"