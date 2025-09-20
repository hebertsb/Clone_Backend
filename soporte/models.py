# soporte/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel
from datetime import datetime, timedelta


class TipoSolicitud(models.TextChoices):
    """Tipos de solicitudes que puede hacer un cliente."""
    REPROGRAMACION = 'REPROGRAMACION', 'Solicitud de reprogramación'
    CANCELACION = 'CANCELACION', 'Solicitud de cancelación'
    INFORMACION = 'INFORMACION', 'Solicitud de información'
    QUEJA = 'QUEJA', 'Queja o reclamo'
    SUGERENCIA = 'SUGERENCIA', 'Sugerencia de mejora'
    PROBLEMA_TECNICO = 'PROBLEMA_TECNICO', 'Problema técnico'
    OTRO = 'OTRO', 'Otro tipo de consulta'


class EstadoSolicitud(models.TextChoices):
    """Estados que puede tener una solicitud de soporte."""
    PENDIENTE = 'PENDIENTE', 'Pendiente de revisión'
    EN_PROCESO = 'EN_PROCESO', 'En proceso'
    ESPERANDO_CLIENTE = 'ESPERANDO_CLIENTE', 'Esperando respuesta del cliente'
    RESUELTO = 'RESUELTO', 'Resuelto'
    CERRADO = 'CERRADO', 'Cerrado'
    ESCALADO = 'ESCALADO', 'Escalado a supervisor'


class PrioridadSolicitud(models.TextChoices):
    """Prioridades para las solicitudes."""
    BAJA = 'BAJA', 'Baja'
    MEDIA = 'MEDIA', 'Media'
    ALTA = 'ALTA', 'Alta'
    CRITICA = 'CRITICA', 'Crítica'


class SolicitudSoporte(TimeStampedModel):
    """
    Modelo principal para gestionar solicitudes de soporte.
    Cada vez que un cliente tiene un problema o quiere reprogramar, se crea una solicitud.
    """
    
    # Información básica
    numero_ticket = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Número único del ticket (generado automáticamente)"
    )
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='solicitudes_soporte',
        help_text="Cliente que realizó la solicitud"
    )
    
    agente_soporte = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_asignadas',
        help_text="Agente de soporte asignado al ticket"
    )
    
    # Detalles de la solicitud
    tipo_solicitud = models.CharField(
        max_length=20,
        choices=TipoSolicitud.choices,
        default=TipoSolicitud.INFORMACION,
        help_text="Tipo de solicitud realizada"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE,
        help_text="Estado actual de la solicitud"
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadSolicitud.choices,
        default=PrioridadSolicitud.MEDIA,
        help_text="Prioridad de la solicitud"
    )
    
    asunto = models.CharField(
        max_length=200,
        help_text="Asunto o título de la solicitud"
    )
    
    descripcion = models.TextField(
        help_text="Descripción detallada de la solicitud"
    )
    
    # Relación con reserva (si aplica)
    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='solicitudes_soporte',
        help_text="Reserva relacionada con la solicitud (opcional)"
    )
    
    # Fechas y tiempos
    fecha_limite_respuesta = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha límite para primera respuesta"
    )
    
    fecha_primera_respuesta = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de la primera respuesta del soporte"
    )
    
    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se resolvió la solicitud"
    )
    
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se cerró la solicitud"
    )
    
    # Metadatos adicionales
    canal_origen = models.CharField(
        max_length=50,
        default='WEB_PANEL',
        help_text="Canal por el cual se originó la solicitud"
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Tags separados por comas para categorización"
    )
    
    satisfaccion_cliente = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} estrella{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="Calificación de satisfacción del cliente (1-5)"
    )
    
    comentario_interno = models.TextField(
        blank=True,
        help_text="Comentarios internos del equipo de soporte"
    )

    class Meta:  # type: ignore
        db_table = 'soporte_solicitud'
        verbose_name = 'Solicitud de Soporte'
        verbose_name_plural = 'Solicitudes de Soporte'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['cliente', 'estado']),
            models.Index(fields=['agente_soporte', 'estado']),
            models.Index(fields=['tipo_solicitud', 'prioridad']),
            models.Index(fields=['created_at']),
            models.Index(fields=['estado', 'prioridad', 'created_at']),
        ]

    def __str__(self):
        return f"#{self.numero_ticket} - {self.asunto} ({self.estado})"
    
    def save(self, *args, **kwargs):
        """Generar número de ticket automáticamente si no existe."""
        if not self.numero_ticket:
            self.numero_ticket = self.generar_numero_ticket()
        
        # Establecer fecha límite de respuesta automáticamente
        if not self.fecha_limite_respuesta and self.created_at:
            self.fecha_limite_respuesta = self.calcular_fecha_limite_respuesta()
        
        # Marcar fecha de primera respuesta si cambia a EN_PROCESO
        if (self.pk and self.estado == EstadoSolicitud.EN_PROCESO 
            and not self.fecha_primera_respuesta):
            self.fecha_primera_respuesta = timezone.now()
        
        # Marcar fecha de resolución si cambia a RESUELTO
        if (self.pk and self.estado == EstadoSolicitud.RESUELTO 
            and not self.fecha_resolucion):
            self.fecha_resolucion = timezone.now()
        
        # Marcar fecha de cierre si cambia a CERRADO
        if (self.pk and self.estado == EstadoSolicitud.CERRADO 
            and not self.fecha_cierre):
            self.fecha_cierre = timezone.now()
        
        super().save(*args, **kwargs)
    
    def generar_numero_ticket(self):
        """Genera un número único de ticket."""
        import uuid
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:6].upper()  # Reducido a 6 caracteres
        return f"SOP-{timestamp}-{unique_id}"
    
    def calcular_fecha_limite_respuesta(self):
        """Calcula fecha límite de respuesta según prioridad."""
        from datetime import timedelta
        
        if not self.created_at:
            base_time = timezone.now()
        else:
            base_time = self.created_at
        
        # Tiempos de respuesta según prioridad
        tiempos_respuesta = {
            PrioridadSolicitud.CRITICA: timedelta(hours=2),
            PrioridadSolicitud.ALTA: timedelta(hours=8),
            PrioridadSolicitud.MEDIA: timedelta(hours=24),
            PrioridadSolicitud.BAJA: timedelta(hours=48),
        }
        
        return base_time + tiempos_respuesta.get(
            PrioridadSolicitud(self.prioridad), 
            timedelta(hours=24)
        )
    
    @property
    def tiempo_respuesta_sla(self):
        """Calcula si se cumplió el SLA de tiempo de respuesta."""
        if not self.fecha_primera_respuesta or not self.fecha_limite_respuesta:
            return None
        
        return self.fecha_primera_respuesta <= self.fecha_limite_respuesta
    
    @property
    def tiempo_total_resolucion(self):
        """Calcula el tiempo total de resolución en horas."""
        if not self.fecha_resolucion:
            return None
        
        base_time = self.created_at or timezone.now()
        delta = self.fecha_resolucion - base_time
        return round(delta.total_seconds() / 3600, 2)
    
    @property
    def esta_vencido(self):
        """Verifica si la solicitud está vencida."""
        if (self.estado in [EstadoSolicitud.RESUELTO, EstadoSolicitud.CERRADO] 
            or not self.fecha_limite_respuesta):
            return False
        
        return timezone.now() > self.fecha_limite_respuesta
    
    def asignar_agente(self, agente):
        """Asigna un agente de soporte a la solicitud."""
        self.agente_soporte = agente
        if self.estado == EstadoSolicitud.PENDIENTE:
            self.estado = EstadoSolicitud.EN_PROCESO
        self.save()
    
    def marcar_como_resuelto(self):
        """Marca la solicitud como resuelta."""
        self.estado = EstadoSolicitud.RESUELTO
        self.fecha_resolucion = timezone.now()
        self.save()
    
    def cerrar_solicitud(self):
        """Cierra la solicitud definitivamente."""
        self.estado = EstadoSolicitud.CERRADO
        self.fecha_cierre = timezone.now()
        self.save()


class MensajeSoporte(TimeStampedModel):
    """
    Modelo para gestionar mensajes entre cliente y soporte.
    Permite conversación bidireccional en tiempo real.
    """
    
    solicitud = models.ForeignKey(
        SolicitudSoporte,
        on_delete=models.CASCADE,
        related_name='mensajes',
        help_text="Solicitud a la que pertenece este mensaje"
    )
    
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        help_text="Usuario que envió el mensaje"
    )
    
    mensaje = models.TextField(
        help_text="Contenido del mensaje"
    )
    
    es_interno = models.BooleanField(
        default=False,
        help_text="Si es True, solo lo ve el equipo de soporte"
    )
    
    leido_por_cliente = models.BooleanField(
        default=False,
        help_text="Si el cliente ha leído este mensaje"
    )
    
    leido_por_soporte = models.BooleanField(
        default=False,
        help_text="Si el equipo de soporte ha leído este mensaje"
    )
    
    fecha_lectura_cliente = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que el cliente leyó el mensaje"
    )
    
    fecha_lectura_soporte = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que soporte leyó el mensaje"
    )
    
    # Archivos adjuntos (opcional)
    archivo_adjunto = models.FileField(
        upload_to='soporte/adjuntos/%Y/%m/',
        null=True,
        blank=True,
        help_text="Archivo adjunto al mensaje"
    )
    
    nombre_archivo_original = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre original del archivo adjunto"
    )

    class Meta:  # type: ignore
        db_table = 'soporte_mensaje'
        verbose_name = 'Mensaje de Soporte'
        verbose_name_plural = 'Mensajes de Soporte'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['solicitud', 'created_at']),
            models.Index(fields=['remitente', 'created_at']),
            models.Index(fields=['leido_por_cliente', 'leido_por_soporte']),
        ]

    def __str__(self):
        return f"Mensaje de {self.remitente.get_full_name()} - {self.solicitud.numero_ticket}"
    
    def save(self, *args, **kwargs):
        """Guardar nombre original del archivo si hay adjunto."""
        if self.archivo_adjunto and not self.nombre_archivo_original:
            self.nombre_archivo_original = self.archivo_adjunto.name
        
        super().save(*args, **kwargs)
    
    @property
    def es_del_cliente(self):
        """Verifica si el mensaje fue enviado por el cliente."""
        return self.remitente == self.solicitud.cliente
    
    @property
    def es_del_soporte(self):
        """Verifica si el mensaje fue enviado por el soporte."""
        return (self.remitente != self.solicitud.cliente and 
                hasattr(self.remitente, 'groups') and
                self.remitente.groups.filter(name='Soporte').exists())
    
    def marcar_como_leido_por_cliente(self):
        """Marca el mensaje como leído por el cliente."""
        if not self.leido_por_cliente:
            self.leido_por_cliente = True
            self.fecha_lectura_cliente = timezone.now()
            self.save(update_fields=['leido_por_cliente', 'fecha_lectura_cliente'])
    
    def marcar_como_leido_por_soporte(self):
        """Marca el mensaje como leído por el soporte."""
        if not self.leido_por_soporte:
            self.leido_por_soporte = True
            self.fecha_lectura_soporte = timezone.now()
            self.save(update_fields=['leido_por_soporte', 'fecha_lectura_soporte'])


class ConfiguracionSoporte(TimeStampedModel):
    """
    Configuraciones generales del sistema de soporte.
    """
    
    # Tiempos de respuesta SLA por prioridad (en horas)
    tiempo_respuesta_critica = models.IntegerField(
        default=2,
        help_text="Tiempo máximo de respuesta para prioridad crítica (horas)"
    )
    
    tiempo_respuesta_alta = models.IntegerField(
        default=8,
        help_text="Tiempo máximo de respuesta para prioridad alta (horas)"
    )
    
    tiempo_respuesta_media = models.IntegerField(
        default=24,
        help_text="Tiempo máximo de respuesta para prioridad media (horas)"
    )
    
    tiempo_respuesta_baja = models.IntegerField(
        default=48,
        help_text="Tiempo máximo de respuesta para prioridad baja (horas)"
    )
    
    # Configuraciones de notificaciones
    enviar_emails_cliente = models.BooleanField(
        default=True,
        help_text="Enviar emails de notificación a clientes"
    )
    
    enviar_emails_soporte = models.BooleanField(
        default=False,
        help_text="Enviar emails de notificación al equipo de soporte"
    )
    
    # Configuraciones de auto-asignación
    asignacion_automatica = models.BooleanField(
        default=True,
        help_text="Asignar automáticamente solicitudes a agentes disponibles"
    )
    
    max_solicitudes_por_agente = models.IntegerField(
        default=10,
        help_text="Máximo de solicitudes activas por agente"
    )
    
    # Configuraciones de cierre automático
    dias_auto_cierre_resueltas = models.IntegerField(
        default=7,
        help_text="Días para cerrar automáticamente solicitudes resueltas"
    )
    
    recordatorio_cliente_dias = models.IntegerField(
        default=3,
        help_text="Días para enviar recordatorio al cliente en solicitudes pendientes"
    )

    class Meta:  # type: ignore
        db_table = 'soporte_configuracion'
        verbose_name = 'Configuración de Soporte'
        verbose_name_plural = 'Configuraciones de Soporte'

    def __str__(self):
        return f"Configuración de Soporte - {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def obtener_configuracion(cls):
        """Obtiene la configuración activa o crea una por defecto."""
        config, created = cls.objects.get_or_create(pk=1)
        return config