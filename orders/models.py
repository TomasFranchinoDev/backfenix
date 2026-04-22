# orders/models.py
import uuid
from django.db import models
from django.utils.crypto import get_random_string
from users.models import Cliente  # <-- Importamos el Cliente de la otra app

def generar_codigo_orden():
    # Genera un código legible tipo "ORD-A1B2C3" para usar en WhatsApp
    return f"ORD-{get_random_string(6).upper()}"

class Orden(models.Model):
    ESTADOS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PREPARACION', 'En Preparación'),
        ('LISTO', 'Listo para envío/retiro'),
        ('DESPACHADO', 'Despachado'),
        ('CANCELADA', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_orden = models.CharField(max_length=20, unique=True, default=generar_codigo_orden, editable=False)
    
    # Vinculamos la orden al Cliente importado
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordenes')
    
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='PENDIENTE')
    
    # Snapshot del carrito
    detalle_carrito = models.JSONField(help_text="Snapshot inmutable de los productos y variantes seleccionadas")
    
    # El total se calcula en el backend antes de guardar
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    notas_cliente = models.TextField(blank=True, help_text="Aclaraciones extra antes de ir a WhatsApp")
    direccion_entrega = models.TextField(blank=True, default="")
    telefono_contacto = models.CharField(max_length=50, blank=True, default="")
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo_orden} - {self.cliente.empresa or self.cliente.nombre_completo} - {self.estado}"
