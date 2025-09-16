from django.contrib import admin
from .models import Descuento

@admin.register(Descuento)
class DescuentoAdmin(admin.ModelAdmin):
    list_display = ('codigo','tipo','valor','fecha_inicio','fecha_fin','estado','created_at')
    list_filter = ('tipo','estado')
    search_fields = ('codigo',)
