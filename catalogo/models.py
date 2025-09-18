from django.db import models
from core.models import TimeStampedModel

# Clase para representar la categoría de un servicio
class Categoria(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


# Clase para representar un servicio
class Servicio(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, default="")
    tipo = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="servicios")  
    dias = models.IntegerField(default=1)  # Proveemos un valor predeterminado
    descripcion_servicio = models.TextField(default="")
    incluido = models.JSONField(default=list)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    visible_publico = models.BooleanField(default=True)
    imagenes = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo



# Clase para representar el itinerario
class Itinerario(TimeStampedModel):
    dia = models.IntegerField()
    titulo = models.CharField(max_length=255)
    actividades = models.JSONField()  # Guardamos las actividades como un JSON array
    # servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="itinerarios", blank=True, null=True)  # Relación con servicio
    # paquete = models.ForeignKey("Paquete", on_delete=models.CASCADE, related_name="itinerarios", blank=True, null=True)  # Relación con paquete

    def __str__(self):
        return f"Día {self.dia}: {self.titulo}"



class Paquete(TimeStampedModel):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    descripcion_corta = models.TextField()
    descripcion_completa = models.TextField()
    calificacion = models.DecimalField(max_digits=2, decimal_places=1)
    numero_reseñas = models.IntegerField()
    precio = models.CharField(max_length=100)
    precio_original = models.CharField(max_length=100)
    duracion = models.CharField(max_length=100)
    max_personas = models.IntegerField()
    dificultad = models.CharField(max_length=100)
    imagenes = models.JSONField()  # Lista de URLs de imágenes
    servicios = models.ManyToManyField(Servicio)  # Relación con servicios
    itinerario = models.ManyToManyField(Itinerario, related_name="paquetes")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="paquetes", default=1)  # Valor predeterminado
    incluido = models.JSONField()  # Lista de elementos incluidos
    no_incluido = models.JSONField()  # Lista de elementos no incluidos
    fechas_disponibles = models.JSONField()  # Lista de fechas disponibles
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nombre


