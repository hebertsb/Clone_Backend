from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from django.db.models.query import QuerySet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from authz.models import Usuario
import logging
from typing import List, Any, Dict, cast

from .models import Reserva, Acompanante, ReservaAcompanante, HistorialReprogramacion
from .serializers import (
    ReservaSerializer, AcompananteSerializer, ReservaAcompananteSerializer,
    ReprogramacionReservaSerializer, ReservaConHistorialSerializer, HistorialReprogramacionSerializer
)
from .notifications import NotificacionReprogramacion

logger = logging.getLogger(__name__)

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

    def get_user_roles(self) -> List[str]:
        user = self.request.user
        # Verificar que el usuario sea una instancia de nuestro modelo Usuario personalizado
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            try:
                return list(user.roles.values_list('nombre', flat=True))
            except AttributeError:
                pass
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
        """Acción mejorada para reprogramar reservas con validaciones completas"""
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para reprogramar reservas.")
        
        reserva = self.get_object()
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            raise PermissionDenied("No puedes reprogramar una reserva que no es tuya.")
        
        # Usar el serializador de reprogramación para validaciones
        serializer = ReprogramacionReservaSerializer(
            data=request.data, 
            context={'request': request, 'reserva': reserva}
        )
        serializer.is_valid(raise_exception=True)
        
        nueva_fecha = serializer.validated_data['nueva_fecha']
        motivo = serializer.validated_data.get('motivo', '')
        
        # Verificar disponibilidad usando método específico
        if not self._is_fecha_disponible(nueva_fecha, reserva):
            return Response(
                {"detail": "La nueva fecha no está disponible."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Realizar reprogramación en transacción
        with transaction.atomic():
            fecha_anterior = reserva.fecha_inicio
            
            # Guardar fecha original si es la primera reprogramación
            if not reserva.fecha_original:
                reserva.fecha_original = fecha_anterior
            
            # Actualizar reserva
            reserva.fecha_inicio = nueva_fecha
            reserva.estado = 'REPROGRAMADA'
            reserva.fecha_reprogramacion = timezone.now()
            reserva.motivo_reprogramacion = motivo
            reserva.numero_reprogramaciones += 1
            reserva.reprogramado_por = request.user
            reserva.save()
            
            # Crear entrada en historial
            historial = HistorialReprogramacion.objects.create(
                reserva=reserva,
                fecha_anterior=fecha_anterior,
                fecha_nueva=nueva_fecha,
                motivo=motivo,
                reprogramado_por=request.user
            )
            
            # Enviar notificaciones
            notificacion_cliente = NotificacionReprogramacion.notificar_cliente(
                reserva, fecha_anterior, motivo
            )
            notificacion_soporte = NotificacionReprogramacion.notificar_administrador(
                reserva, fecha_anterior, request.user, motivo
            )
            
            # Marcar si las notificaciones fueron enviadas
            historial.notificacion_enviada = notificacion_cliente and notificacion_soporte
            historial.save()
        
        # Usar el serializador con historial para la respuesta
        response_serializer = ReservaConHistorialSerializer(reserva)
        
        logger.info(f"Reserva {reserva.id} reprogramada por usuario {request.user.id} de {fecha_anterior} a {nueva_fecha}")
        
        return Response({
            "detail": "Reserva reprogramada con éxito.",
            "reserva": response_serializer.data,
            "notificaciones_enviadas": {
                "cliente": notificacion_cliente,
                "soporte": notificacion_soporte
            }
        }, status=status.HTTP_200_OK)
    
    def _is_fecha_disponible(self, nueva_fecha, reserva_actual):
        """Verificar disponibilidad de la nueva fecha"""
        # Obtener servicios de la reserva actual
        servicios_ids = list(reserva_actual.detalles.values_list('servicio_id', flat=True))
        
        # Buscar reservas conflictivas en la nueva fecha
        reservas_conflictivas = Reserva.objects.filter(
            fecha_inicio__date=nueva_fecha.date(),
            estado__in=['PENDIENTE', 'PAGADA', 'REPROGRAMADA'],
            detalles__servicio_id__in=servicios_ids
        ).exclude(id=reserva_actual.id)
        
        if reservas_conflictivas.exists():
            # Verificar capacidad de los servicios/paquetes
            for detalle in reserva_actual.detalles.all():
                servicio = detalle.servicio
                # Si el servicio está asociado a un paquete, verificar cupo
                if hasattr(servicio, 'paquetes') and servicio.paquetes.exists():
                    paquete = servicio.paquetes.first()
                    if hasattr(paquete, 'max_personas'):
                        # Contar personas ya reservadas para esa fecha
                        personas_reservadas = sum([
                            rs.cantidad for rs in reservas_conflictivas.filter(
                                detalles__servicio=servicio
                            ).values_list('detalles__cantidad', flat=True)
                        ])
                        
                        if personas_reservadas + detalle.cantidad > paquete.max_personas:
                            return False
        
        return True

    @action(detail=True, methods=["get"], url_path="historial-reprogramaciones")
    def historial_reprogramaciones(self, request, pk=None):
        """Obtener el historial de reprogramaciones de una reserva"""
        roles = self.get_user_roles()
        reserva = self.get_object()
        
        # Solo el propietario o admin/operador pueden ver el historial
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            if not any(r in roles for r in ['ADMIN', 'OPERADOR']):
                raise PermissionDenied("No tienes permisos para ver este historial.")
        
        historial = reserva.historial_reprogramaciones.all()
        serializer = HistorialReprogramacionSerializer(historial, many=True)
        
        return Response({
            "reserva_id": reserva.id,
            "numero_reprogramaciones": reserva.numero_reprogramaciones,
            "historial": serializer.data
        })

    @action(detail=True, methods=["get"], url_path="puede-reprogramar")
    def puede_reprogramar(self, request, pk=None):
        """Verificar si una reserva puede ser reprogramada"""
        reserva = self.get_object()
        serializer = ReservaConHistorialSerializer(reserva)
        
        return Response({
            "puede_reprogramar": serializer.data['puede_reprogramar'],
            "numero_reprogramaciones": reserva.numero_reprogramaciones,
            "limite_reprogramaciones": 3,
            "estado_actual": reserva.estado,
            "fecha_actual": reserva.fecha_inicio
        })

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


class GestionReprogramacionAPIView(APIView):
    """Vista API para operaciones avanzadas de reprogramación"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_roles(self) -> List[str]:
        user = self.request.user
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            try:
                return list(user.roles.values_list('nombre', flat=True))
            except AttributeError:
                pass
        return []
    
    def post(self, request, reserva_id):
        """Reprogramar una reserva con validaciones completas"""
        # Obtener la reserva
        reserva = get_object_or_404(Reserva, id=reserva_id)
        
        # Verificar permisos
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para reprogramar reservas.")
        
        if 'CLIENTE' in roles and reserva.usuario != request.user:
            raise PermissionDenied("No puedes reprogramar una reserva que no es tuya.")
        
        # Validar datos de entrada
        serializer = ReprogramacionReservaSerializer(
            data=request.data, 
            context={'request': request, 'reserva': reserva}
        )
        serializer.is_valid(raise_exception=True)
        
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        nueva_fecha = validated_data['nueva_fecha']
        motivo = validated_data.get('motivo', '')
        
        # Verificaciones adicionales de negocio
        try:
            with transaction.atomic():
                # Verificar disponibilidad
                if not self._verificar_disponibilidad_completa(nueva_fecha, reserva):
                    return Response({
                        "error": "FECHA_NO_DISPONIBLE",
                        "detail": "La nueva fecha no está disponible para todos los servicios de la reserva."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Verificar cambios de precio si aplican
                cambio_precio = self._verificar_cambio_precio(nueva_fecha, reserva)
                
                fecha_anterior = reserva.fecha_inicio
                
                # Actualizar reserva
                if not reserva.fecha_original:
                    reserva.fecha_original = fecha_anterior
                
                reserva.fecha_inicio = nueva_fecha
                reserva.estado = 'REPROGRAMADA'
                reserva.fecha_reprogramacion = timezone.now()
                reserva.motivo_reprogramacion = motivo
                reserva.numero_reprogramaciones += 1
                reserva.reprogramado_por = request.user
                
                # Actualizar precio si cambió
                if cambio_precio['cambio']:
                    reserva.total = cambio_precio['nuevo_total']
                
                reserva.save()
                
                # Crear entrada en historial
                historial = HistorialReprogramacion.objects.create(
                    reserva=reserva,
                    fecha_anterior=fecha_anterior,
                    fecha_nueva=nueva_fecha,
                    motivo=motivo,
                    reprogramado_por=request.user
                )
                
                # Enviar notificaciones
                notificacion_cliente = NotificacionReprogramacion.notificar_cliente(
                    reserva, fecha_anterior, motivo
                )
                notificacion_soporte = NotificacionReprogramacion.notificar_administrador(
                    reserva, fecha_anterior, request.user, motivo
                )
                
                historial.notificacion_enviada = notificacion_cliente and notificacion_soporte
                historial.save()
                
                logger.info(f"Reprogramación exitosa - Reserva {reserva.pk} por usuario {request.user.pk}")
                
                return Response({
                    "success": True,
                    "message": "Reserva reprogramada exitosamente",
                    "reserva": ReservaConHistorialSerializer(reserva).data,
                    "cambio_precio": cambio_precio,
                    "notificaciones": {
                        "cliente": notificacion_cliente,
                        "soporte": notificacion_soporte
                    }
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error en reprogramación de reserva {reserva_id}: {str(e)}")
            return Response({
                "error": "ERROR_INTERNO",
                "detail": "Ocurrió un error al procesar la reprogramación. Intenta nuevamente."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_disponibilidad_completa(self, nueva_fecha, reserva):
        """Verificación completa de disponibilidad incluyendo cupos y restricciones"""
        try:
            servicios_reserva = reserva.detalles.all()
            
            for detalle in servicios_reserva:
                servicio = detalle.servicio
                cantidad_solicitada = detalle.cantidad
                
                # Verificar si el servicio tiene restricciones de fecha
                if hasattr(servicio, 'fechas_disponibles') and servicio.fechas_disponibles:
                    # Aquí puedes agregar lógica específica para fechas disponibles
                    pass
                
                # Verificar cupo en paquetes
                if hasattr(servicio, 'paquetes'):
                    for paquete in servicio.paquetes.all():
                        if hasattr(paquete, 'max_personas') and paquete.max_personas:
                            # Contar reservas existentes para esa fecha
                            reservas_existentes = Reserva.objects.filter(
                                fecha_inicio__date=nueva_fecha.date(),
                                estado__in=['PENDIENTE', 'PAGADA', 'REPROGRAMADA'],
                                detalles__servicio__paquetes=paquete
                            ).exclude(id=reserva.id)
                            
                            personas_reservadas = sum([
                                rs.cantidad for rs in reservas_existentes.values_list('detalles__cantidad', flat=True)
                            ])
                            
                            if personas_reservadas + cantidad_solicitada > paquete.max_personas:
                                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {str(e)}")
            return False
    
    def _verificar_cambio_precio(self, nueva_fecha, reserva):
        """Verificar si hay cambios de precio para la nueva fecha"""
        try:
            cambio = False
            nuevo_total = reserva.total
            detalles_cambio = []
            
            for detalle in reserva.detalles.all():
                servicio = detalle.servicio
                precio_actual = detalle.precio_unitario
                precio_nuevo = servicio.costo  # Precio base actual del servicio
                
                # Aquí puedes agregar lógica para precios especiales por fecha
                # Por ejemplo, verificar descuentos temporales o precios de temporada alta
                
                if precio_nuevo != precio_actual:
                    cambio = True
                    diferencia = (precio_nuevo - precio_actual) * detalle.cantidad
                    nuevo_total += diferencia
                    
                    detalles_cambio.append({
                        'servicio': servicio.titulo,
                        'precio_anterior': float(precio_actual),
                        'precio_nuevo': float(precio_nuevo),
                        'cantidad': detalle.cantidad,
                        'diferencia': float(diferencia)
                    })
            
            return {
                'cambio': cambio,
                'nuevo_total': nuevo_total,
                'total_anterior': reserva.total,
                'diferencia_total': nuevo_total - reserva.total,
                'detalles': detalles_cambio
            }
            
        except Exception as e:
            logger.error(f"Error verificando cambio de precio: {str(e)}")
            return {
                'cambio': False,
                'nuevo_total': reserva.total,
                'total_anterior': reserva.total,
                'diferencia_total': 0,
                'detalles': []
            }


# ============================================================================
# VISTAS PARA GESTIÓN DE REGLAS DE REPROGRAMACIÓN
# ============================================================================

class ReglasReprogramacionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar reglas de reprogramación - Solo administradores."""
    
    from .models import ReglasReprogramacion
    from .serializers import ReglasReprogramacionSerializer
    
    queryset = ReglasReprogramacion.objects.all().order_by('prioridad', 'tipo_regla')
    serializer_class = ReglasReprogramacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_roles(self) -> List[str]:
        """Obtiene los roles del usuario actual."""
        user = self.request.user
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            try:
                return list(user.roles.values_list('nombre', flat=True))
            except AttributeError:
                pass
        return []
    
    def check_admin_permission(self):
        """Verifica que el usuario sea administrador."""
        roles = self.get_user_roles()
        if 'ADMIN' not in roles:
            raise PermissionDenied("Solo los administradores pueden gestionar reglas de reprogramación.")
    
    def list(self, request, *args, **kwargs):
        """Lista todas las reglas - Solo admins pueden ver todas."""
        self.check_admin_permission()
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Crear nueva regla - Solo administradores."""
        self.check_admin_permission()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Actualizar regla - Solo administradores."""
        self.check_admin_permission()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar regla - Solo administradores."""
        self.check_admin_permission()
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Obtiene solo las reglas activas."""
        self.check_admin_permission()
        reglas_activas = self.queryset.filter(activa=True)
        serializer = self.get_serializer(reglas_activas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Agrupa reglas por tipo."""
        self.check_admin_permission()
        from .models import ReglasReprogramacion
        
        tipos = {}
        for regla in self.queryset.filter(activa=True):
            tipo = regla.tipo_regla
            if tipo not in tipos:
                tipos[tipo] = []
            tipos[tipo].append(self.get_serializer(regla).data)
        
        return Response(tipos)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa una regla específica."""
        self.check_admin_permission()
        regla = self.get_object()
        regla.activa = True
        regla.save()
        return Response({'detail': f'Regla {regla.nombre} activada exitosamente.'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactiva una regla específica."""
        self.check_admin_permission()
        regla = self.get_object()
        regla.activa = False
        regla.save()
        return Response({'detail': f'Regla {regla.nombre} desactivada exitosamente.'})
    
    @action(detail=False, methods=['post'])
    def validar_configuracion(self, request):
        """Valida toda la configuración de reglas."""
        self.check_admin_permission()
        from .models import ReglasReprogramacion
        
        errores = []
        warnings = []
        
        # Verificar conflictos entre reglas
        reglas_activas = ReglasReprogramacion.objects.filter(activa=True)
        
        # Verificar tiempo mínimo vs máximo
        tiempo_min = ReglasReprogramacion.obtener_valor_regla('TIEMPO_MINIMO', default=0)
        tiempo_max = ReglasReprogramacion.obtener_valor_regla('TIEMPO_MAXIMO', default=float('inf'))
        
        if (tiempo_min and tiempo_max and 
            isinstance(tiempo_min, (int, float)) and isinstance(tiempo_max, (int, float)) and
            tiempo_min >= tiempo_max):
            errores.append("El tiempo mínimo no puede ser mayor o igual al tiempo máximo.")
        
        # Verificar límites razonables
        limite_reprog = ReglasReprogramacion.obtener_valor_regla('LIMITE_REPROGRAMACIONES', default=3)
        if limite_reprog and isinstance(limite_reprog, (int, float)) and limite_reprog > 10:
            warnings.append(f"El límite de {limite_reprog} reprogramaciones parece excesivo.")
        
        # Verificar reglas duplicadas
        tipos_vistos = {}
        for regla in reglas_activas:
            clave = f"{regla.tipo_regla}-{regla.aplicable_a}"
            if clave in tipos_vistos:
                errores.append(f"Regla duplicada: {regla.tipo_regla} para {regla.aplicable_a}")
            tipos_vistos[clave] = regla
        
        return Response({
            'valida': len(errores) == 0,
            'errores': errores,
            'warnings': warnings,
            'total_reglas_activas': reglas_activas.count()
        })


class ConfiguracionGlobalViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar configuraciones globales del sistema."""
    
    from .models import ConfiguracionGlobalReprogramacion
    from .serializers import ConfiguracionGlobalSerializer
    
    queryset = ConfiguracionGlobalReprogramacion.objects.all().order_by('clave')
    serializer_class = ConfiguracionGlobalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_roles(self) -> List[str]:
        """Obtiene los roles del usuario actual."""
        user = self.request.user
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            try:
                return list(user.roles.values_list('nombre', flat=True))
            except AttributeError:
                pass
        return []
    
    def check_admin_permission(self):
        """Verifica que el usuario sea administrador."""
        roles = self.get_user_roles()
        if 'ADMIN' not in roles:
            raise PermissionDenied("Solo los administradores pueden gestionar configuraciones globales.")
    
    def list(self, request, *args, **kwargs):
        """Lista todas las configuraciones."""
        self.check_admin_permission()
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Crear nueva configuración."""
        self.check_admin_permission()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Actualizar configuración."""
        self.check_admin_permission()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar configuración."""
        self.check_admin_permission()
        return super().destroy(request, *args, **kwargs)


class ValidadorReglasAPIView(APIView):
    """Vista para validar si una reprogramación cumple con las reglas configuradas."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Valida una reprogramación contra todas las reglas activas.
        
        Body:
        {
            "reserva_id": 123,
            "nueva_fecha": "2025-10-15T14:30:00Z",
            "motivo": "Cambio por motivos familiares"
        }
        """
        from .serializers import ValidadorReglasSerializer
        
        serializer = ValidadorReglasSerializer(data=request.data, context={'request': request})
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                'valida': True,
                'message': 'La reprogramación cumple con todas las reglas configuradas.',
                'datos_validados': serializer.validated_data
            })
        except ValidationError as e:
            return Response({
                'valida': False,
                'errores': e.detail,
                'message': 'La reprogramación viola una o más reglas configuradas.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResumenReglasAPIView(APIView):
    """Vista para obtener un resumen de todas las reglas aplicables al usuario actual."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna un resumen de todas las reglas activas aplicables al usuario.
        """
        from .serializers import ResumenReglasSerializer
        
        # El serializer no necesita una instancia específica
        serializer = ResumenReglasSerializer(context={'request': request})
        data = serializer.to_representation(None)
        
        return Response(data)


class GestionConfiguracionAPIView(APIView):
    """Vista para gestión avanzada de configuraciones del sistema."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_roles(self) -> List[str]:
        """Obtiene los roles del usuario actual."""
        user = self.request.user
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            try:
                return list(user.roles.values_list('nombre', flat=True))
            except AttributeError:
                pass
        return []
    
    def check_admin_permission(self):
        """Verifica que el usuario sea administrador."""
        roles = self.get_user_roles()
        if 'ADMIN' not in roles:
            raise PermissionDenied("Solo los administradores pueden gestionar la configuración del sistema.")
    
    def get(self, request):
        """Obtiene toda la configuración del sistema."""
        self.check_admin_permission()
        
        from .models import ReglasReprogramacion, ConfiguracionGlobalReprogramacion
        
        # Reglas por tipo
        reglas_por_tipo = {}
        for regla in ReglasReprogramacion.objects.filter(activa=True).order_by('prioridad'):
            tipo = regla.tipo_regla
            if tipo not in reglas_por_tipo:
                reglas_por_tipo[tipo] = []
            reglas_por_tipo[tipo].append({
                'id': regla.pk,
                'nombre': regla.nombre,
                'aplicable_a': regla.aplicable_a,
                'valor': regla.obtener_valor(),
                'prioridad': regla.prioridad
            })
        
        # Configuraciones globales
        configuraciones = {}
        for config in ConfiguracionGlobalReprogramacion.objects.filter(activa=True):
            configuraciones[config.clave] = {
                'valor': config.obtener_valor_tipado(),
                'descripcion': config.descripcion,
                'tipo': config.tipo_valor
            }
        
        return Response({
            'reglas_por_tipo': reglas_por_tipo,
            'configuraciones_globales': configuraciones,
            'resumen': {
                'total_reglas_activas': sum(len(reglas) for reglas in reglas_por_tipo.values()),
                'total_configuraciones': len(configuraciones),
                'tipos_reglas_configurados': list(reglas_por_tipo.keys())
            }
        })
    
    @transaction.atomic
    def post(self, request):
        """Crea configuración inicial del sistema."""
        self.check_admin_permission()
        
        from .models import ReglasReprogramacion, ConfiguracionGlobalReprogramacion
        
        # Reglas por defecto
        reglas_default = [
            {
                'nombre': 'Tiempo mínimo estándar',
                'tipo_regla': 'TIEMPO_MINIMO',
                'aplicable_a': 'ALL',
                'valor_numerico': 24,
                'mensaje_error': 'Debe reprogramar con al menos 24 horas de anticipación.'
            },
            {
                'nombre': 'Límite de reprogramaciones',
                'tipo_regla': 'LIMITE_REPROGRAMACIONES',
                'aplicable_a': 'CLIENTE',
                'valor_numerico': 3,
                'mensaje_error': 'Ha alcanzado el límite máximo de 3 reprogramaciones.'
            },
            {
                'nombre': 'Tiempo mínimo admin',
                'tipo_regla': 'TIEMPO_MINIMO',
                'aplicable_a': 'ADMIN',
                'valor_numerico': 12,
                'mensaje_error': 'Administradores pueden reprogramar con 12 horas de anticipación.'
            }
        ]
        
        # Configuraciones por defecto
        configs_default = [
            {
                'clave': 'EMAIL_NOTIFICACIONES',
                'valor': 'true',
                'descripcion': 'Habilitar envío de notificaciones por email',
                'tipo_valor': 'BOOLEAN'
            },
            {
                'clave': 'ADMIN_EMAILS',
                'valor': 'admin@tuagencia.com',
                'descripcion': 'Emails de administradores para notificaciones',
                'tipo_valor': 'LISTA'
            }
        ]
        
        reglas_creadas = 0
        configs_creadas = 0
        
        # Crear reglas
        for regla_data in reglas_default:
            if not ReglasReprogramacion.objects.filter(
                tipo_regla=regla_data['tipo_regla'],
                aplicable_a=regla_data['aplicable_a']
            ).exists():
                ReglasReprogramacion.objects.create(**regla_data)
                reglas_creadas += 1
        
        # Crear configuraciones
        for config_data in configs_default:
            if not ConfiguracionGlobalReprogramacion.objects.filter(
                clave=config_data['clave']
            ).exists():
                ConfiguracionGlobalReprogramacion.objects.create(**config_data)
                configs_creadas += 1
        
        return Response({
            'message': 'Configuración inicial creada exitosamente.',
            'reglas_creadas': reglas_creadas,
            'configuraciones_creadas': configs_creadas
        })
