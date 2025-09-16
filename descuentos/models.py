from decimal import Decimal
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel  # si prefieres, puedes usar models.Model

class Descuento(TimeStampedModel):
    TIPO = (("PORCENTAJE","PORCENTAJE"),("FIJO","FIJO"))
    codigo = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=12, choices=TIPO)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo

    def aplica_en(self, cuando=None) -> bool:
        ahora = cuando or timezone.now()
        if not self.estado:
            return False
        if self.fecha_inicio and ahora < self.fecha_inicio:
            return False
        if self.fecha_fin and ahora > self.fecha_fin:
            return False
        return True

class ServicioDescuento(TimeStampedModel):
    """Relación entre catálogo.Servicio y un Descuento.
       No toca el modelo Servicio; la relación vive aquí."""
    servicio = models.ForeignKey('catalogo.Servicio', on_delete=models.CASCADE, related_name='servicios_descuento')
    descuento = models.ForeignKey('descuentos.Descuento', on_delete=models.CASCADE, related_name='servicio_descuentos')
    prioridad = models.PositiveSmallIntegerField(default=10, help_text="1 = mayor prioridad")
    exclusivo = models.BooleanField(default=True, help_text="Si es True, corta la cadena de descuentos")
    estado = models.BooleanField(default=True)

    class Meta:
        unique_together = (('servicio','descuento'),)
        ordering = ('prioridad','-id')
        db_table = 'descuentos_servicio_descuento'

    def __str__(self):
        return f"{self.servicio_id} -> {self.descuento.codigo} (p={self.prioridad}, excl={self.exclusivo})"
