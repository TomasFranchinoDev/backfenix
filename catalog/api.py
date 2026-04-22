from django.shortcuts import get_object_or_404
from ninja import Router

from catalog.models import Producto
from catalog.schemas import ProductoSchema

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
