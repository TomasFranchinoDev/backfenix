from datetime import datetime
from uuid import UUID
from typing import Optional

from ninja import Schema


class ClienteSchema(Schema):
    id: UUID
    email: str
    nombre_completo: str
    telefono: str
    empresa: str
    creado_en: datetime


class ClienteAdminOut(Schema):
    id: UUID
    email: str
    nombre_completo: str
    telefono: str
    empresa: str


class RegistroClienteIn(Schema):
    nombre_completo: str
    empresa: Optional[str] = None
    telefono: Optional[str] = None


class ClienteUpdate(Schema):
    nombre_completo: str
    empresa: Optional[str] = None
    telefono: Optional[str] = None
