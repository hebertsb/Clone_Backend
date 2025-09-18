from rest_framework import viewsets
from .models import Categoria, Servicio, Itinerario, Paquete  # Reemplazado 'Destino' por 'Servicio'
from .serializers import CategoriaSerializer, ServicioSerializer, ItinerarioSerializer, PaqueteSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class ItinerarioViewSet(viewsets.ModelViewSet):
    queryset = Itinerario.objects.all()
    serializer_class = ItinerarioSerializer

class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = Paquete.objects.all()  # Si estás usando prefetch_related, asegúrate de que no esté sobrecargado
    serializer_class = PaqueteSerializer
