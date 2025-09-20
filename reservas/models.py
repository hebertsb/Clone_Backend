from django.db import models
from core.models import TimeStampedModel
from authz.models import Usuario
from catalogo.models import Servicio
from cupones.models import Cupon

class Reserva(TimeStampedModel):
    ESTADO = (("PENDIENTE", "PENDIENTE"), ("PAGADA", "PAGADA"), ("CANCELADA", "CANCELADA"), ("REPROGRAMADA", "REPROGRAMADA"))
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, related_name="reservas")
    fecha_inicio = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=ESTADO, default="PENDIENTE")
    cupon = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservas")
    total = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, default="BOB")
    
    # Campos específicos para reprogramaciones
    fecha_original = models.DateTimeField(blank=True, null=True, help_text="Fecha original antes de la reprogramación")
    fecha_reprogramacion = models.DateTimeField(blank=True, null=True, help_text="Fecha cuando se hizo la reprogramación")
    motivo_reprogramacion = models.TextField(blank=True, null=True, help_text="Motivo de la reprogramación")
    numero_reprogramaciones = models.PositiveSmallIntegerField(default=0, help_text="Número de veces que se ha reprogramado")
    reprogramado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name="reservas_reprogramadas", 
                                        help_text="Usuario que hizo la reprogramación")
    
    class Meta(TimeStampedModel.Meta):
        indexes = [
            models.Index(fields=["usuario"]), 
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_inicio"]),
            models.Index(fields=["fecha_reprogramacion"])
        ]

class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="detalles")
    servicio = models.ForeignKey(Servicio, on_delete=models.RESTRICT)
    cantidad = models.PositiveSmallIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_servicio = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = (("reserva", "servicio"),)

class Acompanante(TimeStampedModel):
    documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=191, blank=True, null=True)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    class Meta(TimeStampedModel.Meta):
        db_table = 'reservas_visitante'

class ReservaAcompanante(models.Model):
    ESTADO = (("CONFIRMADO","CONFIRMADO"),("CANCELADO","CANCELADO"))
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="acompanantes")
    acompanante = models.ForeignKey(
        Acompanante,
        on_delete=models.RESTRICT,
        related_name="reservas_acompanantes",
        db_column="visitante_id",
    )
    estado = models.CharField(max_length=10, choices=ESTADO, default="CONFIRMADO")
    es_titular = models.BooleanField(default=False)
    # Garantiza un solo titular por reserva:
    class Meta:
        unique_together = (("reserva","acompanante"),)
        constraints = [
            models.UniqueConstraint(
                fields=["reserva"],
                condition=models.Q(es_titular=True),
                name="uq_un_titular_por_reserva",
            ),
        ]
        db_table = 'reservas_reservavisitante'


class HistorialReprogramacion(TimeStampedModel):
    """Historial de todas las reprogramaciones de una reserva"""
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="historial_reprogramaciones")
    fecha_anterior = models.DateTimeField(help_text="Fecha anterior de la reserva")
    fecha_nueva = models.DateTimeField(help_text="Nueva fecha de la reserva")
    motivo = models.TextField(blank=True, null=True, help_text="Motivo de la reprogramación")
    reprogramado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                        help_text="Usuario que realizó la reprogramación")
    notificacion_enviada = models.BooleanField(default=False, help_text="Si se envió notificación por email")
    
    class Meta(TimeStampedModel.Meta):
        ordering = ['-created_at']
        verbose_name = "Historial de Reprogramación"
        verbose_name_plural = "Historiales de Reprogramación"


class ReglasReprogramacion(TimeStampedModel):
    """
    Modelo para configurar las reglas y políticas de reprogramación.
    Permite definir restricciones dinámicas que se aplican al sistema.
    """
    
    # Identificadores únicos de reglas
    TIPOS_REGLA = (
        ('TIEMPO_MINIMO', 'Tiempo mínimo de anticipación'),
        ('TIEMPO_MAXIMO', 'Tiempo máximo para reprogramar'),
        ('LIMITE_REPROGRAMACIONES', 'Límite de reprogramaciones por reserva'),
        ('LIMITE_DIARIO', 'Límite de reprogramaciones por día'),
        ('LIMITE_SEMANAL', 'Límite de reprogramaciones por semana'),
        ('LIMITE_MENSUAL', 'Límite de reprogramaciones por mes'),
        ('DIAS_BLACKOUT', 'Días no permitidos para reprogramar'),
        ('HORAS_BLACKOUT', 'Horas no permitidas para reprogramar'),
        ('CAPACIDAD_MAXIMA', 'Capacidad máxima por fecha'),
        ('DESCUENTO_PENALIZACION', 'Penalización por reprogramar'),
        ('SERVICIOS_RESTRINGIDOS', 'Servicios con restricciones especiales'),
        ('ROLES_EXCLUIDOS', 'Roles excluidos de ciertas restricciones'),
    )
    
    # Aplicabilidad por roles
    ROLES_APLICABLES = (
        ('ALL', 'Todos los roles'),
        ('CLIENTE', 'Solo clientes'),
        ('OPERADOR', 'Solo operadores'),
        ('ADMIN', 'Solo administradores'),
        ('CLIENTE_OPERADOR', 'Clientes y operadores'),
        ('OPERADOR_ADMIN', 'Operadores y administradores'),
    )
    
    nombre = models.CharField(max_length=100, help_text="Nombre descriptivo de la regla")
    tipo_regla = models.CharField(max_length=30, choices=TIPOS_REGLA, 
                                 help_text="Tipo de regla a aplicar")
    aplicable_a = models.CharField(max_length=20, choices=ROLES_APLICABLES, default='ALL',
                                  help_text="A qué roles se aplica esta regla")
    
    # Valores configurables
    valor_numerico = models.IntegerField(null=True, blank=True, 
                                        help_text="Valor numérico (horas, días, cantidad, etc.)")
    valor_decimal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text="Valor decimal (porcentajes, montos, etc.)")
    valor_texto = models.TextField(null=True, blank=True,
                                  help_text="Valores de texto o JSON (días, horas específicas, etc.)")
    valor_booleano = models.BooleanField(null=True, blank=True,
                                        help_text="Valor verdadero/falso")
    
    # Configuraciones avanzadas
    fecha_inicio_vigencia = models.DateTimeField(null=True, blank=True,
                                                help_text="Cuando empieza a aplicar esta regla")
    fecha_fin_vigencia = models.DateTimeField(null=True, blank=True,
                                             help_text="Cuando deja de aplicar esta regla")
    
    activa = models.BooleanField(default=True, help_text="Si la regla está activa")
    prioridad = models.PositiveSmallIntegerField(default=1, 
                                               help_text="Prioridad de aplicación (1=máxima)")
    mensaje_error = models.TextField(null=True, blank=True,
                                    help_text="Mensaje personalizado cuando se viola la regla")
    
    # Condiciones adicionales
    condiciones_extras = models.JSONField(default=dict, blank=True,
                                         help_text="Condiciones adicionales en formato JSON")
    
    class Meta(TimeStampedModel.Meta):
        ordering = ['prioridad', 'tipo_regla']
        verbose_name = "Regla de Reprogramación"
        verbose_name_plural = "Reglas de Reprogramación"
        indexes = [
            models.Index(fields=['tipo_regla', 'activa']),
            models.Index(fields=['aplicable_a', 'activa']),
            models.Index(fields=['prioridad']),
        ]
        
        # Evitar reglas duplicadas del mismo tipo para el mismo rol
        unique_together = [['tipo_regla', 'aplicable_a']]
    
    def __str__(self):
        # Django genera automáticamente get_tipo_regla_display() para campos con choices
        return f"{self.get_tipo_regla_display()} - {self.nombre}"  # type: ignore
    
    def es_aplicable_a_rol(self, rol):
        """Verifica si esta regla se aplica al rol dado."""
        if self.aplicable_a == 'ALL':
            return True
        elif self.aplicable_a == rol:
            return True
        elif self.aplicable_a == 'CLIENTE_OPERADOR' and rol in ['CLIENTE', 'OPERADOR']:
            return True
        elif self.aplicable_a == 'OPERADOR_ADMIN' and rol in ['OPERADOR', 'ADMIN']:
            return True
        return False
    
    def obtener_valor(self):
        """Retorna el valor configurado según el tipo de dato."""
        if self.valor_numerico is not None:
            return self.valor_numerico
        elif self.valor_decimal is not None:
            return float(self.valor_decimal)
        elif self.valor_booleano is not None:
            return self.valor_booleano
        elif self.valor_texto:
            # Intentar parsear como JSON, si falla retornar como texto
            try:
                import json
                return json.loads(self.valor_texto)
            except:
                return self.valor_texto
        return None
    
    @classmethod
    def obtener_regla_activa(cls, tipo_regla, rol='ALL'):
        """Obtiene la regla activa de mayor prioridad para un tipo y rol específico."""
        reglas = cls.objects.filter(
            tipo_regla=tipo_regla,
            activa=True
        ).order_by('prioridad')
        
        for regla in reglas:
            if regla.es_aplicable_a_rol(rol):
                return regla
        return None
    
    @classmethod
    def obtener_valor_regla(cls, tipo_regla, rol='ALL', default=None):
        """Obtiene el valor de una regla específica."""
        regla = cls.obtener_regla_activa(tipo_regla, rol)
        return regla.obtener_valor() if regla else default
    
    def clean(self):
        """Validación personalizada del modelo."""
        from django.core.exceptions import ValidationError
        
        # Validar que al menos un valor esté definido
        valores = [self.valor_numerico, self.valor_decimal, self.valor_texto, self.valor_booleano]
        if all(v is None or v == '' for v in valores):
            raise ValidationError("Debe definir al menos un valor para la regla.")
        
        # Validar fechas de vigencia
        if (self.fecha_inicio_vigencia and self.fecha_fin_vigencia and 
            self.fecha_inicio_vigencia >= self.fecha_fin_vigencia):
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ConfiguracionGlobalReprogramacion(TimeStampedModel):
    """
    Configuración global del sistema de reprogramaciones.
    Configuraciones que afectan el comportamiento general.
    """
    
    clave = models.CharField(max_length=50, unique=True, 
                            help_text="Clave única de configuración")
    valor = models.TextField(help_text="Valor de la configuración")
    descripcion = models.TextField(help_text="Descripción de qué hace esta configuración")
    tipo_valor = models.CharField(max_length=20, choices=[
        ('STRING', 'Texto'),
        ('INTEGER', 'Número entero'),
        ('DECIMAL', 'Número decimal'),
        ('BOOLEAN', 'Verdadero/Falso'),
        ('JSON', 'JSON/Objeto'),
        ('LISTA', 'Lista de valores'),
    ], default='STRING')
    
    activa = models.BooleanField(default=True)
    
    class Meta(TimeStampedModel.Meta):
        ordering = ['clave']
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuraciones Globales"
    
    def __str__(self):
        return f"{self.clave}: {self.valor[:50]}"
    
    def obtener_valor_tipado(self):
        """Convierte el valor al tipo correcto."""
        if self.tipo_valor == 'INTEGER':
            return int(self.valor)
        elif self.tipo_valor == 'DECIMAL':
            return float(self.valor)
        elif self.tipo_valor == 'BOOLEAN':
            return self.valor.lower() in ['true', '1', 'yes', 'si']
        elif self.tipo_valor == 'JSON':
            import json
            return json.loads(self.valor)
        elif self.tipo_valor == 'LISTA':
            return [item.strip() for item in self.valor.split(',')]
        return self.valor
    
    @classmethod
    def obtener_configuracion(cls, clave, default=None):
        """Obtiene una configuración específica."""
        try:
            config = cls.objects.get(clave=clave, activa=True)
            return config.obtener_valor_tipado()
        except cls.DoesNotExist:
            return default
