from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from authz.views import RolViewSet, UsuarioViewSet
from catalogo.views import CategoriaViewSet, ServicioViewSet, ItinerarioViewSet, PaqueteViewSet
from reservas.views import ReservaViewSet, AcompananteViewSet, ReservaAcompananteViewSet
# from cupones.views import CuponViewSet  # Commented out until CuponViewSet is implemented
from descuentos.views import DescuentoViewSet, ServicioDescuentoViewSet, precio_servicio

router = DefaultRouter()
router.register(r"roles", RolViewSet)
router.register(r"usuarios", UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'servicios', ServicioViewSet)  
router.register(r'itinerarios', ItinerarioViewSet)
router.register(r'paquetes', PaqueteViewSet)
router.register(r"reservas", ReservaViewSet)
router.register(r"acompanantes", AcompananteViewSet)
router.register(r"reserva-acompanantes", ReservaAcompananteViewSet)
# router.register(r"cupones", CuponViewSet)  # Commented out until CuponViewSet is implemented
router.register(r'descuentos', DescuentoViewSet, basename='descuento')
router.register(r'servicios-descuentos', ServicioDescuentoViewSet, basename='servicio-descuento')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/", include(router.urls)),
    path("api/auth/", include("authz.auth_urls")),  # lo creamos abajo
    path("api/autenticacion/", include("authz.auth_urls")),
    path('api/servicios/<int:pk>/precio/', precio_servicio, name='precio-servicio'),
]
