from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, decorators, response, status
from catalogo.models import Servicio
from .models import Descuento, ServicioDescuento
from .serializers import DescuentoSerializer, ServicioDescuentoSerializer
from django.db.models import Q
from django.db import models
from .permissions import IsOperadorOrReadOnly  # 👈 NUEVO

class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all().order_by('-created_at')
    serializer_class = DescuentoSerializer
    permission_classes = [IsOperadorOrReadOnly]       # 👈 NUEVO

class ServicioDescuentoViewSet(viewsets.ModelViewSet):
    queryset = ServicioDescuento.objects.select_related('servicio','descuento').all()
    serializer_class = ServicioDescuentoSerializer
    permission_classes = [IsOperadorOrReadOnly]       # 👈 NUEVO

@decorators.api_view(["GET"])
def precio_servicio(request, pk: int):
    try:
        servicio = Servicio.objects.get(pk=pk)
    except Servicio.DoesNotExist:
        return response.Response({"detail":"Servicio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    ahora = timezone.now()
    precio = Decimal(servicio.costo or 0).quantize(Decimal("0.01"))
    aplicados = []

    qs = (ServicioDescuento.objects
          .filter(servicio=servicio, estado=True, descuento__estado=True)
          .filter(models.Q(descuento__fecha_inicio__isnull=True) | models.Q(descuento__fecha_inicio__lte=ahora))
          .filter(models.Q(descuento__fecha_fin__isnull=True) | models.Q(descuento__fecha_fin__gte=ahora))
          .select_related("descuento")
          .order_by("prioridad","id"))

    for sd in qs:
        d = sd.descuento
        antes = precio
        if d.tipo == "PORCENTAJE":
            precio = (precio * (Decimal("100") - d.valor) / Decimal("100")).quantize(Decimal("0.01"))
        else:  # FIJO
            precio = max(Decimal("0.00"), (precio - d.valor).quantize(Decimal("0.01")))
        aplicados.append({
            "codigo": d.codigo, "tipo": d.tipo, "valor": str(d.valor),
            "exclusivo": sd.exclusivo, "antes": str(antes), "despues": str(precio)
        })
        if sd.exclusivo:
            break

    return response.Response({
        "servicio": servicio.id,
        "costo_base": str(servicio.costo),
        "aplicados": aplicados,
        "precio_final": str(precio),
    })
