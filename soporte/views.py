# soporte/views.py

from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth.models import Group, User
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    SolicitudSoporte, 
    MensajeSoporte, 
    ConfiguracionSoporte,
    EstadoSolicitud,
    TipoSolicitud,
    PrioridadSolicitud
)
from .serializers import (
    SolicitudSoporteListSerializer,
    SolicitudSoporteDetailSerializer,
    CrearSolicitudSoporteSerializer,
    GestionSolicitudSoporteSerializer,
    MensajeSoporteSerializer,
    DashboardSoporteSerializer,
    EstadisticasClienteSerializer,
    ConfiguracionSoporteSerializer
)
from .permissions import EsSoporte, EsClienteOSoporte, EsCliente


class SolicitudSoporteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar solicitudes de soporte.
    
    - Clientes: pueden crear y ver sus propias solicitudes
    - Soporte: puede ver todas las solicitudes y gestionarlas
    """
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_solicitud', 'estado', 'prioridad', 'agente_soporte']
    search_fields = ['numero_ticket', 'asunto', 'descripcion', 'cliente__username', 'cliente__email']
    ordering_fields = ['created_at', 'updated_at', 'prioridad', 'fecha_limite_respuesta']
    ordering = ['-created_at']
    
    def get_queryset(self):  # type: ignore
        """Filtrar solicitudes según el tipo de usuario."""
        user = self.request.user
        
        if user.groups.filter(name='Soporte').exists():
            # Soporte ve todas las solicitudes
            return SolicitudSoporte.objects.select_related(
                'cliente', 'agente_soporte', 'reserva'
            ).prefetch_related('mensajes')
        else:
            # Clientes solo ven sus propias solicitudes
            return SolicitudSoporte.objects.filter(
                cliente=user
            ).select_related(
                'agente_soporte', 'reserva'
            ).prefetch_related('mensajes')
    
    def get_serializer_class(self):  # type: ignore
        """Seleccionar serializer según la acción."""
        if self.action == 'create':
            return CrearSolicitudSoporteSerializer
        elif self.action in ['update', 'partial_update'] and self.request.user.groups.filter(name='Soporte').exists():
            return GestionSolicitudSoporteSerializer
        elif self.action == 'retrieve':
            return SolicitudSoporteDetailSerializer
        else:
            return SolicitudSoporteListSerializer
    
    def get_permissions(self):
        """Permisos según la acción."""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy', 'asignar_agente', 'cambiar_estado']:
            permission_classes = [EsSoporte]
        else:
            permission_classes = [EsClienteOSoporte]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[EsSoporte])
    def asignar_agente(self, request, pk=None):
        """Asignar un agente específico a la solicitud."""
        solicitud = self.get_object()
        agente_id = request.data.get('agente_id')
        
        try:
            agente = User.objects.get(id=agente_id)
            if not agente.groups.filter(name='Soporte').exists():
                return Response(
                    {'error': 'El usuario no pertenece al equipo de soporte'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            solicitud.asignar_agente(agente)
            
            return Response({
                'message': f'Solicitud asignada a {agente.get_full_name()}',
                'agente': {
                    'id': agente.id,
                    'nombre': agente.get_full_name(),
                    'email': agente.email
                }
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Agente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[EsSoporte])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de la solicitud."""
        solicitud = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in [choice[0] for choice in EstadoSolicitud.choices]:
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estado_anterior = solicitud.estado
        solicitud.estado = nuevo_estado
        
        # Lógica especial según el nuevo estado
        if nuevo_estado == EstadoSolicitud.RESUELTO:
            solicitud.marcar_como_resuelto()
        elif nuevo_estado == EstadoSolicitud.CERRADO:
            solicitud.cerrar_solicitud()
        else:
            solicitud.save()
        
        return Response({
            'message': f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            'estado_anterior': estado_anterior,
            'estado_nuevo': nuevo_estado,
            'fecha_cambio': solicitud.updated_at
        })
    
    @action(detail=False, methods=['get'], permission_classes=[EsSoporte])
    def dashboard(self, request):
        """Dashboard con estadísticas para el equipo de soporte."""
        hoy = timezone.now().date()
        hace_7_dias = hoy - timedelta(days=7)
        
        # Métricas básicas
        solicitudes_pendientes = SolicitudSoporte.objects.filter(
            estado=EstadoSolicitud.PENDIENTE
        ).count()
        
        solicitudes_en_proceso = SolicitudSoporte.objects.filter(
            estado=EstadoSolicitud.EN_PROCESO
        ).count()
        
        solicitudes_vencidas = SolicitudSoporte.objects.filter(
            fecha_limite_respuesta__lt=timezone.now(),
            estado__in=[EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROCESO]
        ).count()
        
        solicitudes_resueltas_hoy = SolicitudSoporte.objects.filter(
            fecha_resolucion__date=hoy
        ).count()
        
        # Tiempos promedio
        solicitudes_con_respuesta = SolicitudSoporte.objects.filter(
            fecha_primera_respuesta__isnull=False,
            created_at__gte=hace_7_dias
        )
        
        tiempo_promedio_respuesta = 0
        if solicitudes_con_respuesta.exists():
            tiempos_respuesta = []
            for sol in solicitudes_con_respuesta:
                if sol.fecha_primera_respuesta and sol.created_at:
                    delta = sol.fecha_primera_respuesta - sol.created_at
                    tiempos_respuesta.append(delta.total_seconds() / 3600)
            
            if tiempos_respuesta:
                tiempo_promedio_respuesta = sum(tiempos_respuesta) / len(tiempos_respuesta)
        
        solicitudes_resueltas = SolicitudSoporte.objects.filter(
            fecha_resolucion__isnull=False,
            created_at__gte=hace_7_dias
        )
        
        tiempo_promedio_resolucion = 0
        if solicitudes_resueltas.exists():
            tiempos_resolucion = [sol.tiempo_total_resolucion for sol in solicitudes_resueltas if sol.tiempo_total_resolucion]
            if tiempos_resolucion:
                tiempo_promedio_resolucion = sum(tiempos_resolucion) / len(tiempos_resolucion)
        
        # Satisfacción promedio
        satisfaccion_promedio = SolicitudSoporte.objects.filter(
            satisfaccion_cliente__isnull=False,
            created_at__gte=hace_7_dias
        ).aggregate(
            promedio=Avg('satisfaccion_cliente')
        )['promedio'] or 0
        
        # Distribución por tipo
        solicitudes_por_tipo = dict(
            SolicitudSoporte.objects.filter(
                created_at__gte=hace_7_dias
            ).values('tipo_solicitud').annotate(
                count=Count('id')
            ).values_list('tipo_solicitud', 'count')
        )
        
        # Distribución por prioridad
        solicitudes_por_prioridad = dict(
            SolicitudSoporte.objects.filter(
                created_at__gte=hace_7_dias
            ).values('prioridad').annotate(
                count=Count('id')
            ).values_list('prioridad', 'count')
        )
        
        # Carga por agente
        agentes_soporte = User.objects.filter(
            groups__name='Soporte',
            is_active=True
        )
        
        carga_por_agente = []
        for agente in agentes_soporte:
            solicitudes_activas = agente.solicitudes_asignadas.filter(  # type: ignore
                estado__in=[EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROCESO, EstadoSolicitud.ESPERANDO_CLIENTE]
            ).count()
            
            carga_por_agente.append({
                'agente': agente.get_full_name(),
                'solicitudes_activas': solicitudes_activas,
                'email': agente.email
            })
        
        # Tendencia semanal
        tendencia_semanal = []
        for i in range(7):
            fecha = hoy - timedelta(days=i)
            count = SolicitudSoporte.objects.filter(
                created_at__date=fecha
            ).count()
            tendencia_semanal.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'solicitudes': count
            })
        
        tendencia_semanal.reverse()
        
        data = {
            'solicitudes_pendientes': solicitudes_pendientes,
            'solicitudes_en_proceso': solicitudes_en_proceso,
            'solicitudes_vencidas': solicitudes_vencidas,
            'solicitudes_resueltas_hoy': solicitudes_resueltas_hoy,
            'tiempo_promedio_respuesta': round(tiempo_promedio_respuesta, 2),
            'tiempo_promedio_resolucion': round(tiempo_promedio_resolucion, 2),
            'satisfaccion_promedio': round(satisfaccion_promedio, 2),
            'solicitudes_por_tipo': solicitudes_por_tipo,
            'solicitudes_por_prioridad': solicitudes_por_prioridad,
            'carga_por_agente': carga_por_agente,
            'tendencia_semanal': tendencia_semanal
        }
        
        serializer = DashboardSoporteSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_estadisticas(self, request):
        """Estadísticas personales del cliente."""
        user = request.user
        hace_30_dias = timezone.now() - timedelta(days=30)
        
        total_solicitudes = SolicitudSoporte.objects.filter(cliente=user).count()
        
        solicitudes_abiertas = SolicitudSoporte.objects.filter(
            cliente=user,
            estado__in=[EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROCESO, EstadoSolicitud.ESPERANDO_CLIENTE]
        ).count()
        
        solicitudes_resueltas = SolicitudSoporte.objects.filter(
            cliente=user,
            estado=EstadoSolicitud.RESUELTO
        ).count()
        
        # Tiempo promedio de resolución
        solicitudes_con_resolucion = SolicitudSoporte.objects.filter(
            cliente=user,
            tiempo_total_resolucion__isnull=False
        )
        
        tiempo_promedio_resolucion = 0
        if solicitudes_con_resolucion.exists():
            tiempos = [sol.tiempo_total_resolucion for sol in solicitudes_con_resolucion if sol.tiempo_total_resolucion is not None]
            if tiempos:
                tiempo_promedio_resolucion = sum(tiempos) / len(tiempos)
        
        # Satisfacción promedio
        satisfaccion_promedio = SolicitudSoporte.objects.filter(
            cliente=user,
            satisfaccion_cliente__isnull=False
        ).aggregate(
            promedio=Avg('satisfaccion_cliente')
        )['promedio'] or 0
        
        # Última actividad
        ultima_solicitud = SolicitudSoporte.objects.filter(cliente=user).first()
        ultima_actividad = ultima_solicitud.updated_at if ultima_solicitud else None
        
        # Solicitudes recientes
        solicitudes_recientes = SolicitudSoporte.objects.filter(
            cliente=user,
            created_at__gte=hace_30_dias
        )[:5]
        
        data = {
            'total_solicitudes': total_solicitudes,
            'solicitudes_abiertas': solicitudes_abiertas,
            'solicitudes_resueltas': solicitudes_resueltas,
            'tiempo_promedio_resolucion': round(tiempo_promedio_resolucion, 2),
            'satisfaccion_promedio': round(satisfaccion_promedio, 2),
            'ultima_actividad': ultima_actividad,
            'solicitudes_recientes': solicitudes_recientes
        }
        
        serializer = EstadisticasClienteSerializer(data)
        return Response(serializer.data)


class MensajeSoporteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mensajes de soporte.
    """
    
    serializer_class = MensajeSoporteSerializer
    permission_classes = [EsClienteOSoporte]
    filter_backends = [OrderingFilter]
    ordering = ['created_at']
    
    def get_queryset(self):  # type: ignore
        """Filtrar mensajes según solicitud y permisos."""
        solicitud_id = self.kwargs.get('solicitud_pk')
        user = self.request.user
        
        try:
            solicitud = SolicitudSoporte.objects.get(id=solicitud_id)
            
            # Verificar permisos
            if user == solicitud.cliente or user.groups.filter(name='Soporte').exists():
                queryset = MensajeSoporte.objects.filter(solicitud=solicitud)
                
                # Si es cliente, no mostrar mensajes internos
                if user == solicitud.cliente:
                    queryset = queryset.filter(es_interno=False)
                
                return queryset.select_related('remitente', 'solicitud')
            else:
                return MensajeSoporte.objects.none()
                
        except SolicitudSoporte.DoesNotExist:
            return MensajeSoporte.objects.none()
    
    def perform_create(self, serializer):
        """Crear mensaje asociándolo a la solicitud correcta."""
        solicitud_id = self.kwargs.get('solicitud_pk')
        try:
            solicitud = SolicitudSoporte.objects.get(id=solicitud_id)
            serializer.save(
                solicitud=solicitud,
                remitente=self.request.user
            )
        except SolicitudSoporte.DoesNotExist:
            raise serializers.ValidationError("Solicitud no encontrada")
    
    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, solicitud_pk=None, pk=None):
        """Marcar mensaje como leído."""
        mensaje = self.get_object()
        user = request.user
        
        if user == mensaje.solicitud.cliente:
            mensaje.marcar_como_leido_por_cliente()
        elif user.groups.filter(name='Soporte').exists():
            mensaje.marcar_como_leido_por_soporte()
        
        return Response({'message': 'Mensaje marcado como leído'})
    
    @action(detail=False, methods=['post'])
    def marcar_todos_leidos(self, request, solicitud_pk=None):
        """Marcar todos los mensajes de la solicitud como leídos."""
        user = request.user
        mensajes = self.get_queryset()
        
        if user.groups.filter(name='Soporte').exists():
            # Marcar como leídos por soporte
            mensajes.filter(leido_por_soporte=False).update(
                leido_por_soporte=True,
                fecha_lectura_soporte=timezone.now()
            )
        else:
            # Marcar como leídos por cliente
            mensajes.filter(leido_por_cliente=False).update(
                leido_por_cliente=True,
                fecha_lectura_cliente=timezone.now()
            )
        
        return Response({'message': 'Todos los mensajes marcados como leídos'})


class ConfiguracionSoporteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar configuración del sistema de soporte.
    Solo accesible por administradores.
    """
    
    queryset = ConfiguracionSoporte.objects.all()
    serializer_class = ConfiguracionSoporteSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self):  # type: ignore
        """Siempre devolver la configuración principal."""
        return ConfiguracionSoporte.obtener_configuracion()