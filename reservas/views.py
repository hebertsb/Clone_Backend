from rest_framework import viewsets, permissions
from django.db.models.query import QuerySet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from .models import Reserva, Acompanante, ReservaAcompanante
from .serializers import ReservaSerializer, AcompananteSerializer, ReservaAcompananteSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().select_related("usuario", "cupon").prefetch_related("detalles", "acompanantes__acompanante")
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Habilitar filtro por estado usando django-filter
    from django_filters.rest_framework import DjangoFilterBackend
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado"]

    # Estados válidos para edición:
    # "PENDIENTE", "CONFIRMADA", "PAGADA", "CANCELADA", "COMPLETADA"
    # Puedes editar el campo estado a cualquiera de estos valores usando PATCH o PUT.

    def get_user_roles(self):
        user = self.request.user
        # Verifica que el usuario tenga el atributo 'roles'
        if hasattr(user, 'roles'):
            return list(user.roles.values_list('nombre', flat=True))  # type: ignore
        return []

    def get_queryset(self) -> QuerySet:  # type: ignore[reportIncompatibleMethodOverride]
    # Nota: anotación de tipo para ayudar al analizador estático (Pylance).
        roles = self.get_user_roles()
        user = self.request.user
        if 'ADMIN' in roles or 'OPERADOR' in roles:
            return Reserva.objects.all().select_related("usuario", "cupon").prefetch_related("detalles", "acompanantes__acompanante")
        if 'CLIENTE' in roles:
            return Reserva.objects.filter(usuario=user).select_related("usuario", "cupon").prefetch_related("detalles", "acompanantes__acompanante")
        return Reserva.objects.none()

    def perform_create(self, serializer):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para crear reservas.")
        if 'CLIENTE' in roles:
            serializer.save(usuario=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR']):
            raise PermissionDenied("No tienes permisos para actualizar reservas.")
        serializer.save()

    def perform_destroy(self, instance):
        roles = self.get_user_roles()
        if 'ADMIN' not in roles:
            raise PermissionDenied("Solo el rol ADMIN puede eliminar reservas.")
        instance.delete()

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para cancelar reservas.")
        reserva = self.get_object()
        # Solo el titular/propietario o admin/operador pueden cancelar
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            raise PermissionDenied("No puedes cancelar una reserva que no es tuya.")
        reserva.estado = 'CANCELADA'
        reserva.save()
        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=["post"], url_path="pagar")
    def pagar(self, request, pk=None):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para marcar como pagada.")
        reserva = self.get_object()
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            raise PermissionDenied("No puedes pagar una reserva que no es tuya.")
        reserva.estado = 'PAGADA'
        reserva.save()
        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=["post"], url_path="reprogramar")
    def reprogramar(self, request, pk=None):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para reprogramar reservas.")
        reserva = self.get_object()
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            raise PermissionDenied("No puedes reprogramar una reserva que no es tuya.")
        nueva_fecha = request.data.get('fecha_inicio')
        if not nueva_fecha:
            return Response({"detail": "Falta fecha_inicio"}, status=status.HTTP_400_BAD_REQUEST)
        reserva.fecha_inicio = nueva_fecha
        reserva.estado = 'REPROGRAMADA'
        reserva.save()
        return Response(self.get_serializer(reserva).data)

class AcompananteViewSet(viewsets.ModelViewSet):
    queryset = Acompanante.objects.all()
    serializer_class = AcompananteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReservaAcompananteViewSet(viewsets.ModelViewSet):
    queryset = ReservaAcompanante.objects.all()
    serializer_class = ReservaAcompananteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as exc:
            # Normalizar errores de constraint único a un campo consistente
            from django.db import IntegrityError
            from rest_framework.exceptions import ValidationError
            if isinstance(exc, IntegrityError):
                # Mapeo genérico al campo acompanante
                raise ValidationError({"acompanante": "Este acompañante ya está asociado a la reserva."})
            raise
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
