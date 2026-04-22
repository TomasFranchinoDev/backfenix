from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sku', 'precio_base', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'sku')
