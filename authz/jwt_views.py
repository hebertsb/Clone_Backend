from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
import hashlib
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers as drf_serializers

def verify_password(plain, stored_hash):
    # Primero intenta usar el verificador de Django (para contraseñas nuevas)
    try:
        if check_password(plain, stored_hash):
            return True
    except Exception:
        pass
    # Fallback legacy: comparar SHA256
    return hashlib.sha256(plain.encode()).hexdigest() == stored_hash

@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Iniciar sesión",
    description="Autenticación por email y password. Devuelve tokens JWT.",
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "email": drf_serializers.EmailField(),
            "password": drf_serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="LoginResponse",
            fields={
                "access": drf_serializers.CharField(),
                "refresh": drf_serializers.CharField(),
            },
        ),
        401: OpenApiResponse(description="Credenciales inválidas"),
    },
)
def login_view(request):
    print("LOGIN BODY RECIBIDO:", request.data)
    email = request.data.get("email")
    password = request.data.get("password")
    try:
        u = Usuario.objects.get(email=email, estado="ACTIVO")
        print("USUARIO ENCONTRADO:", u.email, "ROLES:", list(u.roles.values_list('nombre', flat=True)))
    except Usuario.DoesNotExist:
        print("NO SE ENCONTRÓ USUARIO:", email)
        return Response({"detail":"Credenciales inválidas"}, status=401)
    if not u.check_password(password):
        print("CONTRASEÑA INCORRECTA para:", email)
        return Response({"detail":"Credenciales inválidas"}, status=401)
    print("LOGIN EXITOSO:", email)
    refresh = RefreshToken.for_user(u)
    return Response({"access": str(refresh.access_token), "refresh": str(refresh)})

@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Renovar token de acceso",
    description="Intercambia un refresh token válido por un nuevo access token.",
    request=inline_serializer(
        name="RefreshRequest",
        fields={
            "refresh": drf_serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="RefreshResponse",
            fields={
                "access": drf_serializers.CharField(),
            },
        ),
        400: OpenApiResponse(description="Falta refresh"),
        401: OpenApiResponse(description="Refresh inválido"),
    },
)
def refresh_view(request):
    token = request.data.get("refresh")
    if not token:
        return Response({"detail":"Falta refresh"}, status=400)
    try:
        r = RefreshToken(token)
        new_access = r.access_token
        return Response({"access": str(new_access)})
    except Exception:
        return Response({"detail":"Refresh inválido"}, status=401)
