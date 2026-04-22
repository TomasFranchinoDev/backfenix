from decimal import Decimal
from typing import Any, List
from uuid import UUID
from typing import Optional, Union
from ninja import Field, Schema

from users.schemas import ClienteAdminOut


class ItemCarritoIn(Schema):
    producto_id: UUID
    cantidad: int = Field(..., ge=1)
    variantes: dict = Field(default_factory=dict)


class OrdenIn(Schema):
    items: List[ItemCarritoIn]
    notas_cliente: str = ""
    direccion_entrega: Optional[str] = None
    telefono_contacto: Optional[str] = None


class OrdenOut(Schema):
    codigo_orden: str
    total: Decimal


class EstadoOrdenUpdate(Schema):
    estado: str


class OrdenAdminUpdate(Schema):
    estado: str
    detalle_carrito: Union[list, dict]
    total: Decimal


class OrdenAdminOut(Schema):
    id: UUID
    codigo_orden: str
    estado: str
    total: Decimal
    detalle_carrito: dict[str, Any]
    notas_cliente: str
    creado_en: str
    cliente: ClienteAdminOut


class MessageOut(Schema):
    detail: str
