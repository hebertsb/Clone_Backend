from django.contrib import admin
from .models import Reserva, ReservaServicio, Acompanante, ReservaAcompanante, HistorialReprogramacion


class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    extra = 0
    readonly_fields = ['precio_unitario']


class ReservaAcompananteInline(admin.TabularInline):
    model = ReservaAcompanante
    extra = 0


class HistorialReprogramacionInline(admin.TabularInline):
    model = HistorialReprogramacion
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'usuario', 'fecha_inicio', 'estado', 'total', 'moneda', 
        'numero_reprogramaciones', 'created_at'
    ]
    list_filter = ['estado', 'moneda', 'numero_reprogramaciones', 'created_at']
    search_fields = ['usuario__nombres', 'usuario__apellidos', 'usuario__email']
    readonly_fields = [
        'fecha_original', 'fecha_reprogramacion', 'numero_reprogramaciones', 
        'reprogramado_por', 'created_at', 'updated_at'
    ]
    inlines = [ReservaServicioInline, ReservaAcompananteInline, HistorialReprogramacionInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'fecha_inicio', 'estado', 'total', 'moneda', 'cupon')
        }),
        ('Reprogramaciones', {
            'fields': (
                'fecha_original', 'fecha_reprogramacion', 'numero_reprogramaciones',
                'motivo_reprogramacion', 'reprogramado_por'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Acompanante)
class AcompananteAdmin(admin.ModelAdmin):
    list_display = ['documento', 'nombre', 'apellido', 'email', 'telefono']
    search_fields = ['documento', 'nombre', 'apellido', 'email']
    list_filter = ['nacionalidad']


@admin.register(ReservaAcompanante)
class ReservaAcompananteAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'acompanante', 'estado', 'es_titular']
    list_filter = ['estado', 'es_titular']
    search_fields = ['reserva__id', 'acompanante__nombre', 'acompanante__apellido']


@admin.register(HistorialReprogramacion)
class HistorialReprogramacionAdmin(admin.ModelAdmin):
    list_display = [
        'reserva', 'fecha_anterior', 'fecha_nueva', 'reprogramado_por', 
        'notificacion_enviada', 'created_at'
    ]
    list_filter = ['notificacion_enviada', 'created_at']
    search_fields = ['reserva__id', 'motivo', 'reprogramado_por__nombres']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información de Reprogramación', {
            'fields': ('reserva', 'fecha_anterior', 'fecha_nueva', 'motivo', 'reprogramado_por')
        }),
        ('Notificaciones', {
            'fields': ('notificacion_enviada',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# ============================================================================
# ADMIN PARA REGLAS DE REPROGRAMACIÓN
# ============================================================================

from .models import ReglasReprogramacion, ConfiguracionGlobalReprogramacion

@admin.register(ReglasReprogramacion)
class ReglasReprogramacionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo_regla', 'aplicable_a', 'valor_display', 
        'activa', 'prioridad', 'created_at'
    ]
    list_filter = [
        'tipo_regla', 'aplicable_a', 'activa', 'prioridad', 'created_at'
    ]
    search_fields = ['nombre', 'mensaje_error']
    ordering = ['prioridad', 'tipo_regla', 'aplicable_a']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo_regla', 'aplicable_a', 'activa', 'prioridad')
        }),
        ('Valores de Configuración', {
            'fields': ('valor_numerico', 'valor_decimal', 'valor_texto', 'valor_booleano'),
            'description': 'Configure solo el tipo de valor necesario según el tipo de regla.'
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio_vigencia', 'fecha_fin_vigencia'),
            'classes': ('collapse',)
        }),
        ('Configuración Avanzada', {
            'fields': ('mensaje_error', 'condiciones_extras'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activar_reglas', 'desactivar_reglas', 'duplicar_reglas']
    
    def valor_display(self, obj):
        """Muestra el valor interpretado de la regla."""
        valor = obj.obtener_valor()
        if valor is None:
            return "No configurado"
        return str(valor)[:50]
    
    valor_display.short_description = "Valor"  # type: ignore
    
    def activar_reglas(self, request, queryset):
        """Acción para activar reglas seleccionadas."""
        count = queryset.update(activa=True)
        self.message_user(request, f"{count} reglas activadas exitosamente.")
    
    activar_reglas.short_description = "Activar reglas seleccionadas"  # type: ignore
    
    def desactivar_reglas(self, request, queryset):
        """Acción para desactivar reglas seleccionadas."""
        count = queryset.update(activa=False)
        self.message_user(request, f"{count} reglas desactivadas exitosamente.")
    
    desactivar_reglas.short_description = "Desactivar reglas seleccionadas"  # type: ignore
    
    def duplicar_reglas(self, request, queryset):
        """Acción para duplicar reglas seleccionadas."""
        count = 0
        for regla in queryset:
            # Crear una copia con nombre modificado
            nueva_regla = ReglasReprogramacion(
                nombre=f"Copia de {regla.nombre}",
                tipo_regla=regla.tipo_regla,
                aplicable_a=regla.aplicable_a,
                valor_numerico=regla.valor_numerico,
                valor_decimal=regla.valor_decimal,
                valor_texto=regla.valor_texto,
                valor_booleano=regla.valor_booleano,
                fecha_inicio_vigencia=regla.fecha_inicio_vigencia,
                fecha_fin_vigencia=regla.fecha_fin_vigencia,
                activa=False,  # Crear desactivada por seguridad
                prioridad=regla.prioridad + 1,
                mensaje_error=regla.mensaje_error,
                condiciones_extras=regla.condiciones_extras
            )
            nueva_regla.save()
            count += 1
        self.message_user(request, f"{count} reglas duplicadas exitosamente (creadas desactivadas).")
    
    duplicar_reglas.short_description = "Duplicar reglas seleccionadas"  # type: ignore


@admin.register(ConfiguracionGlobalReprogramacion)
class ConfiguracionGlobalAdmin(admin.ModelAdmin):
    list_display = [
        'clave', 'valor_display', 'tipo_valor', 'activa', 'updated_at'
    ]
    list_filter = ['tipo_valor', 'activa', 'created_at']
    search_fields = ['clave', 'descripcion', 'valor']
    ordering = ['clave']
    
    fieldsets = (
        ('Configuración', {
            'fields': ('clave', 'valor', 'tipo_valor', 'activa')
        }),
        ('Descripción', {
            'fields': ('descripcion',),
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activar_configs', 'desactivar_configs']
    
    def valor_display(self, obj):
        """Muestra el valor de forma legible."""
        valor = str(obj.valor)
        return valor[:50] + "..." if len(valor) > 50 else valor
    
    valor_display.short_description = "Valor"  # type: ignore
    
    def activar_configs(self, request, queryset):
        """Activar configuraciones seleccionadas."""
        count = queryset.update(activa=True)
        self.message_user(request, f"{count} configuraciones activadas.")
    
    activar_configs.short_description = "Activar configuraciones"  # type: ignore
    
    def desactivar_configs(self, request, queryset):
        """Desactivar configuraciones seleccionadas."""
        count = queryset.update(activa=False)
        self.message_user(request, f"{count} configuraciones desactivadas.")
    
    desactivar_configs.short_description = "Desactivar configuraciones"  # type: ignore
