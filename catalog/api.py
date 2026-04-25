from django.shortcuts import get_object_or_404
from ninja import Router

from catalog.models import Producto
from catalog.schemas import ProductoSchema, ValidarCarritoIn, ValidarCarritoOut

router = Router(tags=["catalog"])


@router.get("/productos", response=list[ProductoSchema])
def listar_productos(request):
    return (
        Producto.objects.filter(activo=True)
        .prefetch_related("imagenes")
        .order_by("nombre")
    )


@router.get("/productos/{slug}", response=ProductoSchema)
def detalle_producto(request, slug: str):
    return get_object_or_404(
        Producto.objects.prefetch_related("imagenes"),
        slug=slug,
        activo=True,
    )


@router.post("/validar-carrito", response=ValidarCarritoOut)
def validar_carrito(request, payload: ValidarCarritoIn):
    requested_ids = list(dict.fromkeys(payload.producto_ids))

    if not requested_ids:
        return {"disponibles": [], "no_disponibles": []}

    available_ids = set(
        Producto.objects.filter(id__in=requested_ids, activo=True).values_list("id", flat=True)
    )

    available_ids_in_order = [producto_id for producto_id in requested_ids if producto_id in available_ids]
    unavailable_ids = [producto_id for producto_id in requested_ids if producto_id not in available_ids]

    return {
        "disponibles": available_ids_in_order,
        "no_disponibles": unavailable_ids,
    }
