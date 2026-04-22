from decimal import Decimal

from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja.schema import Schema

from catalog.models import Producto
from orders.models import Orden
from orders.schemas import OrdenIn, OrdenOut
from users.auth import auth_supabase

router = Router(tags=["orders"], auth=auth_supabase)


class OrdenResumenOut(Schema):
    codigo_orden: str
    estado: str
    total: Decimal
    creado_en: str


@router.post("/crear", response=OrdenOut)
def crear_orden(request, payload: OrdenIn):
    cliente = request.auth
    payload_data = payload.dict(exclude_unset=True)

    if not payload.items:
        raise HttpError(400, "La orden debe incluir al menos un item")

    total = Decimal("0.00")
    snapshot_items = []

    with transaction.atomic():
        for item in payload.items:
            producto = Producto.objects.filter(id=item.producto_id, activo=True).first()
            if not producto:
                raise HttpError(400, f"Producto inválido o inactivo: {item.producto_id}")

            precio_unitario = producto.precio_base
            subtotal = precio_unitario * item.cantidad
            total += subtotal

            snapshot_items.append(
                {
                    "producto_id": str(producto.id),
                    "sku": producto.sku,
                    "nombre": producto.nombre,
                    "precio_unitario": str(precio_unitario),
                    "cantidad": item.cantidad,
                    "variantes": item.variantes,
                    "subtotal": str(subtotal),
                }
            )

        orden = Orden.objects.create(
            cliente=cliente,
            estado="PENDIENTE",
            detalle_carrito={
                "items": snapshot_items,
                "notas_cliente": payload_data.get("notas_cliente", ""),
                "direccion_entrega": payload_data.get("direccion_entrega", ""),
                "telefono_contacto": payload_data.get("telefono_contacto", ""),
            },
            total=total,
            notas_cliente=payload_data.get("notas_cliente", ""),
            direccion_entrega=payload_data.get("direccion_entrega", ""),
            telefono_contacto=payload_data.get("telefono_contacto", ""),
        )

    return OrdenOut(codigo_orden=orden.codigo_orden, total=orden.total)


class OrdenDetalleOut(Schema):
    codigo_orden: str
    estado: str
    total: Decimal
    creado_en: str
    actualizado_en: str
    notas_cliente: str
    direccion_entrega: str
    telefono_contacto: str
    detalle_carrito: dict


@router.get("/mis-ordenes", response=list[OrdenResumenOut])
def mis_ordenes(request):
    cliente = request.auth
    ordenes = (
        Orden.objects.filter(cliente=cliente)
        .order_by("-creado_en")
        .values("codigo_orden", "estado", "total", "creado_en")
    )

    return [
        {
            "codigo_orden": orden["codigo_orden"],
            "estado": orden["estado"],
            "total": orden["total"],
            "creado_en": orden["creado_en"].isoformat(),
        }
        for orden in ordenes
    ]


@router.get("/mis-ordenes/{codigo_orden}", response=OrdenDetalleOut)
def detalle_orden(request, codigo_orden: str):
    cliente = request.auth
    orden = Orden.objects.filter(cliente=cliente, codigo_orden=codigo_orden).first()
    if not orden:
        raise HttpError(404, "Orden no encontrada")

    return {
        "codigo_orden": orden.codigo_orden,
        "estado": orden.estado,
        "total": orden.total,
        "creado_en": orden.creado_en.isoformat(),
        "actualizado_en": orden.actualizado_en.isoformat(),
        "notas_cliente": orden.notas_cliente,
        "direccion_entrega": orden.direccion_entrega,
        "telefono_contacto": orden.telefono_contacto,
        "detalle_carrito": orden.detalle_carrito,
    }
