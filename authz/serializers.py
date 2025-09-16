# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ["id","nombre","created_at","updated_at"]



class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), many=True, required=False)
    class Meta:
        model = Usuario
        fields = ["id", "nombres", "apellidos", "email", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais", "estado", "roles"]



class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = Usuario
        fields = ["nombres", "apellidos", "email", "password", "password_confirm", "telefono", "fecha_nacimiento", "genero", "documento_identidad", "pais"]
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        from .models import Rol
        rol_cliente, _ = Rol.objects.get_or_create(nombre="CLIENTE")
        user.roles.add(rol_cliente)
        return user



class UsuarioRegistroSerializer(UsuarioCreateSerializer):
    pass