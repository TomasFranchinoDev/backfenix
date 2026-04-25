from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from ninja import Field, Schema


class ProductoImagenSchema(Schema):
    id: UUID
    url: str
    es_principal: bool
    orden: int


class ProductoImagenIn(Schema):
    url: str
    es_principal: bool = False
    orden: int = 0


class ProductoSchema(Schema):
    id: UUID
    nombre: str
    descripcion: str
    precio_base: Decimal
    sku: Optional[str] = None
    slug: Optional[str] = None
    esquema_opciones: dict
    imagenes: list[ProductoImagenSchema] = Field(default_factory=list)

    @staticmethod
    def resolve_imagenes(obj):
        return obj.imagenes.all().order_by("orden", "id")


class ProductoIn(Schema):
    nombre: str
    descripcion: str = ""
    precio_base: Decimal = Field(..., ge=0)
    sku: Optional[str] = None
    esquema_opciones: dict[str, Any] = Field(default_factory=dict)
    activo: bool = True
    imagenes: list[ProductoImagenIn] = Field(default_factory=list)
    imagen_principal_url: Optional[str] = None


class ProductoUpdate(Schema):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(default=None, ge=0)
    sku: Optional[str] = None
    esquema_opciones: Optional[dict[str, Any]] = None
    activo: Optional[bool] = None
    imagenes: Optional[list[ProductoImagenIn]] = None
    imagen_principal_url: Optional[str] = None


class ProductoOut(Schema):
    id: UUID
    nombre: str
    descripcion: str
    precio_base: Decimal
    sku: Optional[str] = None
    esquema_opciones: dict[str, Any]
    activo: bool
    imagenes: list[ProductoImagenSchema] = Field(default_factory=list)

    @staticmethod
    def resolve_imagenes(obj):
        return obj.imagenes.all().order_by("orden", "id")


class ValidarCarritoIn(Schema):
    producto_ids: list[UUID] = Field(default_factory=list)


class ValidarCarritoOut(Schema):
    disponibles: list[UUID] = Field(default_factory=list)
    no_disponibles: list[UUID] = Field(default_factory=list)
