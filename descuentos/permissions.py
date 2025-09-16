# descuentos/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOperadorOrReadOnly(BasePermission):
    message = "Solo OPERADOR o ADMIN pueden crear/editar; CLIENTE tiene acceso de lectura."

    def has_permission(self, request, view):
        # Lectura (GET/HEAD/OPTIONS) siempre permitida
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False

        # Superuser siempre permitido
        if getattr(user, "is_superuser", False):
            return True

        # Tu modelo: user.roles (M2M) con campo 'nombre'
        try:
            roles = set(r.upper() for r in user.roles.values_list("nombre", flat=True))
        except Exception:
            roles = set()

        # Solo estos pueden escribir (POST/PUT/PATCH/DELETE)
        return bool(roles & {"OPERADOR", "ADMIN"})

