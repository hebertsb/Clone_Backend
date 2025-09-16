from rest_framework import viewsets, permissions, filters
from .models import Categoria, Servicio
from .serializers import CategoriaSerializer, ServicioSerializer

from .models import Destino, Itinerario, Paquete
from .serializers import DestinoSerializer, ItinerarioSerializer, PaqueteSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "descripcion", "tipo"]
    ordering_fields = ["costo", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET":
            qs = qs.filter(visible_publico=True)
        categoria = self.request.query_params.get("categoria")
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        tipo = self.request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

# ViewSet para Destino
class DestinoViewSet(viewsets.ModelViewSet):
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ViewSet para Itinerario
class ItinerarioViewSet(viewsets.ModelViewSet):
    queryset = Itinerario.objects.all()
    serializer_class = ItinerarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ViewSet para Paquete
class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
