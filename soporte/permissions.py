# soporte/permissions.py

from rest_framework import permissions
from typing import Any


class EsSoporte(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario pertenece al equipo de soporte.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='Soporte').exists()
        )


class EsCliente(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un cliente (no soporte).
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return (
            request.user and 
            request.user.is_authenticated and 
            not request.user.groups.filter(name='Soporte').exists()
        )


class EsClienteOSoporte(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es cliente o soporte.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore
        """
        Verificar permisos a nivel de objeto.
        - Cliente: solo puede acceder a sus propias solicitudes
        - Soporte: puede acceder a todas las solicitudes
        """
        if hasattr(obj, 'cliente'):
            # Es una solicitud de soporte
            return (
                request.user == obj.cliente or 
                request.user.groups.filter(name='Soporte').exists()
            )
        elif hasattr(obj, 'solicitud'):
            # Es un mensaje de soporte
            return (
                request.user == obj.solicitud.cliente or 
                request.user.groups.filter(name='Soporte').exists()
            )
        
        return False


class EsPropietarioOSoporte(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es el propietario del objeto o soporte.
    """
    
    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore
        # El usuario es soporte
        if request.user.groups.filter(name='Soporte').exists():
            return True
        
        # El usuario es el propietario del objeto
        if hasattr(obj, 'cliente'):
            return request.user == obj.cliente
        elif hasattr(obj, 'user'):
            return request.user == obj.user
        elif hasattr(obj, 'owner'):
            return request.user == obj.owner
        
        return False


class PuedeCrearSolicitud(permissions.BasePermission):
    """
    Permiso para verificar si un usuario puede crear solicitudes de soporte.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Los usuarios de soporte pueden crear solicitudes en nombre de clientes
        if request.user.groups.filter(name='Soporte').exists():
            return True
        
        # Los clientes pueden crear sus propias solicitudes
        return True


class PuedeModificarSolicitud(permissions.BasePermission):
    """
    Permiso para verificar si un usuario puede modificar solicitudes de soporte.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore
        # Solo soporte puede modificar solicitudes
        if request.user.groups.filter(name='Soporte').exists():
            return True
        
        # Los clientes solo pueden agregar mensajes, no modificar la solicitud
        if view.action in ['create', 'destroy'] and hasattr(obj, 'solicitud'):
            # Es un mensaje - verificar si es del cliente correcto
            return request.user == obj.solicitud.cliente
        
        return False


class PuedeVerEstadisticas(permissions.BasePermission):
    """
    Permiso para verificar si un usuario puede ver estadísticas.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return request.user and request.user.is_authenticated


class PuedeConfigurarSistema(permissions.BasePermission):
    """
    Permiso para verificar si un usuario puede configurar el sistema de soporte.
    """
    
    def has_permission(self, request, view) -> bool:  # type: ignore
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or 
             request.user.groups.filter(name='Administradores').exists())
        )