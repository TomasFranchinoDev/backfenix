from typing import Optional
from uuid import UUID
import time
import cloudinary
import cloudinary.utils

from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from catalog.models import Producto, ProductoImagen
from catalog.schemas import ProductoIn, ProductoOut, ProductoUpdate
from orders.models import Orden
from orders.schemas import EstadoOrdenUpdate, MessageOut, OrdenAdminOut, OrdenAdminUpdate
from users.auth import auth_admin

router = Router(tags=["admin"], auth=auth_admin)

@router.get("/cloudinary-signature")
def get_cloudinary_signature(request):
    timestamp = int(time.time())
    
    params_to_sign = {
        "timestamp": timestamp,
        "folder": "fenix_productos"
    }
    
    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        cloudinary.config().api_secret
    )
    
    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": cloudinary.config().api_key,
        "cloud_name": cloudinary.config().cloud_name,
        "folder": "fenix_productos"
    }



def _guardar_imagenes_producto(producto: Producto, imagenes_payload: list, imagen_principal_url: Optional[str] = None):
    if not imagenes_payload:
        return

    principal_asignada = False
    for item in imagenes_payload:
        es_principal = item.get("es_principal", False)
        if imagen_principal_url:
            es_principal = item.get("url") == imagen_principal_url

        if es_principal and not principal_asignada:
            principal_asignada = True
        elif es_principal and principal_asignada:
            es_principal = False

        ProductoImagen.objects.create(
            producto=producto,
            url=item.get("url"),
            es_principal=es_principal,
            orden=item.get("orden", 0),
        )

    if not principal_asignada:
        primera_imagen = producto.imagenes.order_by("orden", "id").first()
        if primera_imagen:
            primera_imagen.es_principal = True
            primera_imagen.save(update_fields=["es_principal"])


@router.get("/productos", response=list[ProductoOut])
def listar_productos_admin(request):
    return Producto.objects.prefetch_related("imagenes").order_by("-creado_en")


@router.get("/productos/{producto_id}", response=ProductoOut)
def detalle_producto_admin(request, producto_id: UUID):
    producto = Producto.objects.prefetch_related("imagenes").filter(id=producto_id).first()
    if not producto:
        raise HttpError(404, "Producto no encontrado")
    return producto


@router.post("/productos", response=ProductoOut)
def crear_producto(request, payload: ProductoIn):
    with transaction.atomic():
        data = payload.dict()
        imagenes_payload = data.pop("imagenes", [])
        imagen_principal_url = data.pop("imagen_principal_url", None)

        producto = Producto.objects.create(**data)
        _guardar_imagenes_producto(producto, imagenes_payload, imagen_principal_url)

    return producto


@router.put("/productos/{producto_id}", response=ProductoOut)
def actualizar_producto(request, producto_id: UUID, payload: ProductoUpdate):
    producto = Producto.objects.filter(id=producto_id).first()
    if not producto:
        raise HttpError(404, "Producto no encontrado")

    data = payload.dict(exclude_unset=True)
    if not data:
        raise HttpError(400, "No se enviaron campos para actualizar")

    with transaction.atomic():
        imagenes_payload = data.pop("imagenes", None)
        imagen_principal_url = data.pop("imagen_principal_url", None)

        for field, value in data.items():
            setattr(producto, field, value)

        if data:
            producto.save()

        if imagenes_payload is not None:
            producto.imagenes.all().delete()
            _guardar_imagenes_producto(producto, imagenes_payload, imagen_principal_url)
        elif imagen_principal_url:
            imagenes_actuales = producto.imagenes.all()
            imagenes_actuales.update(es_principal=False)
            principal = imagenes_actuales.filter(url=imagen_principal_url).first()
            if not principal:
                raise HttpError(400, "La imagen principal indicada no existe en el producto")
            principal.es_principal = True
            principal.save(update_fields=["es_principal"])

    return producto


@router.delete("/productos/{producto_id}", response=MessageOut)
def eliminar_producto(request, producto_id: UUID):
    producto = Producto.objects.filter(id=producto_id).first()
    if not producto:
        raise HttpError(404, "Producto no encontrado")

    producto.activo = False
    producto.save(update_fields=["activo", "actualizado_en"])
    return {"detail": "Producto desactivado correctamente"}


@router.get("/ordenes", response=list[OrdenAdminOut])
def listar_ordenes_admin(request):
    ordenes = Orden.objects.select_related("cliente").order_by("-creado_en")
    return [
        {
            "id": orden.id,
            "codigo_orden": orden.codigo_orden,
            "estado": orden.estado,
            "total": orden.total,
            "detalle_carrito": orden.detalle_carrito,
            "notas_cliente": orden.notas_cliente,
            "creado_en": orden.creado_en.isoformat(),
            "cliente": {
                "id": orden.cliente.id,
                "email": orden.cliente.email,
                "nombre_completo": orden.cliente.nombre_completo,
                "telefono": orden.cliente.telefono,
                "empresa": orden.cliente.empresa,
            },
        }
        for orden in ordenes
    ]


@router.get("/ordenes/{orden_id}", response=OrdenAdminOut)
def detalle_orden_admin(request, orden_id: UUID):
    orden = Orden.objects.select_related("cliente").filter(id=orden_id).first()
    if not orden:
        raise HttpError(404, "Orden no encontrada")
    
    return {
        "id": orden.id,
        "codigo_orden": orden.codigo_orden,
        "estado": orden.estado,
        "total": orden.total,
        "detalle_carrito": orden.detalle_carrito,
        "notas_cliente": orden.notas_cliente,
        "creado_en": orden.creado_en.isoformat(),
        "cliente": {
            "id": orden.cliente.id,
            "email": orden.cliente.email,
            "nombre_completo": orden.cliente.nombre_completo,
            "telefono": orden.cliente.telefono,
            "empresa": orden.cliente.empresa,
        },
    }


@router.patch("/ordenes/{orden_id}/estado", response=MessageOut)
def actualizar_estado_orden(request, orden_id: UUID, payload: EstadoOrdenUpdate):
    orden = Orden.objects.filter(id=orden_id).first()
    if not orden:
        raise HttpError(404, "Orden no encontrada")

    estados_validos = {value for value, _ in Orden.ESTADOS_CHOICES}
    if payload.estado not in estados_validos:
        raise HttpError(400, f"Estado inválido. Usa uno de: {', '.join(sorted(estados_validos))}")

    orden.estado = payload.estado
    orden.save(update_fields=["estado", "actualizado_en"])
    return {"detail": "Estado de la orden actualizado correctamente"}


@router.put("/ordenes/{orden_id}", response=MessageOut)
def actualizar_orden_admin(request, orden_id: UUID, payload: OrdenAdminUpdate):
    orden = Orden.objects.filter(id=orden_id).first()
    if not orden:
        raise HttpError(404, "Orden no encontrada")

    estados_validos = {value for value, _ in Orden.ESTADOS_CHOICES}
    if payload.estado not in estados_validos:
        raise HttpError(400, f"Estado inválido. Usa uno de: {', '.join(sorted(estados_validos))}")

    orden.estado = payload.estado
    orden.detalle_carrito = payload.detalle_carrito
    orden.total = payload.total
    orden.save(update_fields=["estado", "detalle_carrito", "total", "actualizado_en"])
    return {"detail": "Orden actualizada correctamente"}
