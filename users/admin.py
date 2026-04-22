from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('email', 'empresa', 'nombre_completo', 'telefono')
    search_fields = ('email', 'empresa')