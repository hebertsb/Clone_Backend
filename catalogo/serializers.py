
from rest_framework import serializers
from .models import Categoria, Servicio, Destino, Itinerario, Paquete

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"

class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = "__all__"

class ItinerarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerario
        fields = "__all__"


class PaqueteSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    destinos = DestinoSerializer(many=True, read_only=True)
    itinerario = ItinerarioSerializer(many=True, read_only=True)
    class Meta:
        model = Paquete
        fields = "__all__"

    max_personas = serializers.IntegerField(read_only=True)
