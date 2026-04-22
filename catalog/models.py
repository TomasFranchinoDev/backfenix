# catalog/models.py
import uuid

from django.db import models
from django.utils.text import slugify

class Producto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Aquí reside la magia dinámica para las variantes (tamaños, manijas, colores)
    esquema_opciones = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Configuración JSON de variantes y recargos. Ej: {\"manijas\": [{\"label\": \"Cordón\", \"extra\": 150}]}"
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre) or "producto"
            slug = base_slug

            if Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{str(self.id)[:8]}"

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class ProductoImagen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
    url = models.URLField(max_length=1024)
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre} - {self.url}"
