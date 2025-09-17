
from django.db import models
from core.models import TimeStampedModel

# Clase para representar la categoría del paquete
class Categoria(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# Modelo Servicio
class Servicio(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, default="")
    tipo = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="servicios")
    visible_publico = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

# Clase para representar el destino del paquete
class Destino(TimeStampedModel):
    nombre = models.CharField(max_length=255)
    dias = models.IntegerField()
    descripcion = models.TextField(default="")
    incluido = models.JSONField(default=list)  # Lista de elementos incluidos
    calificacion = models.DecimalField(max_digits=2, decimal_places=1)
    def __str__(self):
        return self.nombre

# Clase para representar el itinerario de un paquete
class Itinerario(TimeStampedModel):
    dia = models.IntegerField()
    titulo = models.CharField(max_length=255)
    actividades = models.JSONField()  # Guardamos las actividades como un JSON array

    def __str__(self):
        return f"Día {self.dia}: {self.titulo}"

# Clase para representar un paquete turístico
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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagenes = models.JSONField()  # Lista de URLs de imágenes
    destinos = models.ManyToManyField(Destino)
    itinerario = models.ManyToManyField(Itinerario)
    incluido = models.JSONField()  # Lista de elementos incluidos
    no_incluido = models.JSONField()  # Lista de elementos no incluidos
    fechas_disponibles = models.JSONField()  # Lista de fechas disponibles
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nombre
