# soporte/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    SolicitudSoporteViewSet,
    MensajeSoporteViewSet,
    ConfiguracionSoporteViewSet
)

# Router principal
router = DefaultRouter()
router.register(r'solicitudes', SolicitudSoporteViewSet, basename='solicitudes')
router.register(r'configuracion', ConfiguracionSoporteViewSet, basename='configuracion')

# Router anidado para mensajes dentro de solicitudes
solicitudes_router = routers.NestedDefaultRouter(router, r'solicitudes', lookup='solicitud')
solicitudes_router.register(r'mensajes', MensajeSoporteViewSet, basename='solicitud-mensajes')

urlpatterns = [
    # Rutas principales del sistema de soporte
    path('', include(router.urls)),
    
    # Rutas anidadas para mensajes
    path('', include(solicitudes_router.urls)),
    
    # Rutas adicionales específicas
    path('dashboard/', SolicitudSoporteViewSet.as_view({'get': 'dashboard'}), name='soporte-dashboard'),
    path('mis-estadisticas/', SolicitudSoporteViewSet.as_view({'get': 'mis_estadisticas'}), name='soporte-mis-estadisticas'),
]

# Patrones de URL disponibles:
"""
Gestión de Solicitudes:
- GET    /soporte/solicitudes/                    - Listar solicitudes (filtradas por usuario)
- POST   /soporte/solicitudes/                    - Crear nueva solicitud
- GET    /soporte/solicitudes/{id}/               - Detalles de solicitud específica
- PUT    /soporte/solicitudes/{id}/               - Actualizar solicitud (solo soporte)
- PATCH  /soporte/solicitudes/{id}/               - Actualización parcial (solo soporte)
- DELETE /soporte/solicitudes/{id}/               - Eliminar solicitud (solo soporte)

Acciones específicas de solicitudes:
- POST   /soporte/solicitudes/{id}/asignar_agente/     - Asignar agente específico
- POST   /soporte/solicitudes/{id}/cambiar_estado/     - Cambiar estado de solicitud

Gestión de Mensajes:
- GET    /soporte/solicitudes/{id}/mensajes/           - Listar mensajes de solicitud
- POST   /soporte/solicitudes/{id}/mensajes/           - Crear nuevo mensaje
- GET    /soporte/solicitudes/{id}/mensajes/{msg_id}/  - Detalles de mensaje
- PUT    /soporte/solicitudes/{id}/mensajes/{msg_id}/  - Actualizar mensaje
- DELETE /soporte/solicitudes/{id}/mensajes/{msg_id}/  - Eliminar mensaje

Acciones específicas de mensajes:
- POST   /soporte/solicitudes/{id}/mensajes/{msg_id}/marcar_leido/      - Marcar mensaje como leído
- POST   /soporte/solicitudes/{id}/mensajes/marcar_todos_leidos/        - Marcar todos como leídos

Estadísticas y Dashboard:
- GET    /soporte/dashboard/                      - Dashboard completo (solo soporte)
- GET    /soporte/mis-estadisticas/              - Estadísticas personales (clientes)

Configuración del Sistema:
- GET    /soporte/configuracion/                 - Obtener configuración actual
- PUT    /soporte/configuracion/{id}/            - Actualizar configuración (solo admin)
- PATCH  /soporte/configuracion/{id}/            - Actualización parcial configuración

Filtros disponibles en solicitudes:
- ?tipo_solicitud=TECNICO                        - Filtrar por tipo
- ?estado=PENDIENTE                              - Filtrar por estado
- ?prioridad=ALTA                                - Filtrar por prioridad
- ?agente_soporte=1                              - Filtrar por agente asignado
- ?search=problema                               - Búsqueda en texto
- ?ordering=-created_at                          - Ordenamiento
"""