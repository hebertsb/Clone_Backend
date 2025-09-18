from rest_framework import serializers
from .models import Categoria, Servicio, Itinerario, Paquete


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"


class ItinerarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerario
        fields = "__all__"


class PaqueteSerializer(serializers.ModelSerializer):
    itinerario = ItinerarioSerializer(
        many=True, read_only=True
    )  # Asegúrate de incluir el serializer del itinerario

    class Meta:
        model = Paquete
        fields = "__all__"

    max_personas = serializers.IntegerField(read_only=True)
