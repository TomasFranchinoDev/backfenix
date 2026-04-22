# Create your models here.
# users/models.py
from django.db import models

class Cliente(models.Model):
    """
    Este modelo almacena los datos de negocio del usuario.
    El 'id' debe ser provisto directamente por el token JWT de Supabase al momento de crearlo.
    """
    id = models.UUIDField(primary_key=True, editable=False) # Mapea 1:1 con auth.users de Supabase
    email = models.EmailField(unique=True)
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=50, blank=True, help_text="Teléfono para contacto por WhatsApp")
    empresa = models.CharField(max_length=200, blank=True, help_text="Nombre del comercio")
    es_admin = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa or self.nombre_completo} ({self.email})"
