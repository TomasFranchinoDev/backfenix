import logging
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from users.auth import auth_registro, auth_supabase
from users.models import Cliente
from users.schemas import ClienteSchema, RegistroClienteIn, ClienteUpdate

logger = logging.getLogger(__name__)

router = Router(tags=["users"], auth=auth_supabase)


def serialize_cliente(cliente: Cliente) -> dict:
    return {
        "id": cliente.id,
        "email": cliente.email,
        "nombre_completo": cliente.nombre_completo,
        "telefono": cliente.telefono,
        "empresa": cliente.empresa,
        "es_admin": cliente.es_admin,
        "creado_en": cliente.creado_en,
    }


@router.get("/me", response=ClienteSchema)
def mi_perfil(request):
    logger.info(
        "GET /api/users/me auth_header_present=%s auth_payload_sub=%s",
        bool(request.headers.get("Authorization")),
        getattr(request, "auth_payload", {}).get("sub") if hasattr(request, "auth_payload") else None,
    )
    return serialize_cliente(request.auth)


@router.put("/me", response=ClienteSchema)
def actualizar_perfil(request, payload: ClienteUpdate):
    cliente = request.auth
    cliente.nombre_completo = payload.nombre_completo
    cliente.telefono = payload.telefono or ""
    cliente.empresa = payload.empresa or ""
    cliente.save(update_fields=["nombre_completo", "telefono", "empresa"])
    return serialize_cliente(cliente)


@router.post("/registro", auth=auth_registro, response=ClienteSchema)
def registrar_cliente(request, payload: RegistroClienteIn):
    logger.info(
        "POST /api/users/registro auth_header_present=%s auth_payload_sub=%s",
        bool(request.headers.get("Authorization")),
        getattr(request, "auth_payload", {}).get("sub") if hasattr(request, "auth_payload") else None,
    )
    token_payload = request.auth
    user_id = token_payload.get("sub")
    email = token_payload.get("email")

    if not user_id or not email:
        raise HttpError(400, "El token no contiene los datos necesarios para registrar el cliente")

    cliente, created = Cliente.objects.get_or_create(
        id=UUID(user_id),
        defaults={
            "email": email,
            "nombre_completo": payload.nombre_completo,
            "empresa": payload.empresa or "",
            "telefono": payload.telefono or "",
        },
    )

    if not created:
        cliente.email = email
        cliente.nombre_completo = payload.nombre_completo
        cliente.empresa = payload.empresa or ""
        cliente.telefono = payload.telefono or ""
        cliente.save(update_fields=["email", "nombre_completo", "empresa", "telefono"])

    return serialize_cliente(cliente)
