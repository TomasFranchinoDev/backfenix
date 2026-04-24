import logging
import os
from functools import lru_cache

import jwt
from django.conf import settings
from ninja.security import HttpBearer
from ninja.errors import HttpError
from .models import Cliente


logger = logging.getLogger(__name__)


@lru_cache(maxsize=8)
def _get_jwks_client(jwks_url):
    return jwt.PyJWKClient(jwks_url)


def _decode_supabase_token(token):
    unverified_header = jwt.get_unverified_header(token)
    algorithm = unverified_header.get("alg", "HS256")
    asymmetric_algorithms = {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}

    if algorithm in asymmetric_algorithms:
        unverified_payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_iat": False,
                "verify_aud": False,
            },
        )
        issuer = unverified_payload.get("iss")

        if not issuer:
            raise jwt.InvalidTokenError("Token sin issuer (iss)")

        jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
        signing_key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(token).key

        logger.info("Decodificando JWT de Supabase con algoritmo %s via JWKS", algorithm)

        try:
            return jwt.decode(
                token,
                signing_key,
                algorithms=[algorithm],
                audience="authenticated",
                issuer=issuer,
            )
        except jwt.InvalidAudienceError:
            logger.warning(
                "JWT RS con audience inesperado. Reintentando sin validacion estricta de audience"
            )
            return jwt.decode(
                token,
                signing_key,
                algorithms=[algorithm],
                issuer=issuer,
                options={"verify_aud": False},
            )

    if algorithm != "HS256":
        raise jwt.InvalidTokenError(f"Algoritmo JWT no soportado: {algorithm}")

    jwt_secret = (
        os.getenv("SUPABASE_JWT_SECRET")
        or getattr(settings, "SUPABASE_JWT_SECRET", None)
        or ""
    ).strip().strip('"').strip("'")

    if not jwt_secret:
        raise HttpError(500, "SUPABASE_JWT_SECRET no configurado")

    logger.info("Decodificando JWT de Supabase con algoritmo HS256")

    try:
        return jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.InvalidAudienceError:
        logger.warning(
            "JWT con audience inesperado. Reintentando sin validacion estricta de audience"
        )
        return jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )


def _log_auth_request(request, token):
    authorization = request.headers.get("Authorization", "")
    logger.info(
        "Solicitud auth Supabase: has_authorization=%s token_prefix=%s",
        bool(authorization),
        token[:12] if token else "",
    )


class SupabaseAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            _log_auth_request(request, token)
            payload = _decode_supabase_token(token)
            cliente_id = payload.get("sub")
            cliente = Cliente.objects.filter(id=cliente_id).first()
            
            if not cliente:
                # --- NUEVA LÓGICA: Extraer datos del user_metadata ---
                user_metadata = payload.get("user_metadata", {})
                
                cliente = Cliente.objects.create(
                    id=cliente_id,
                    email=payload.get("email", ""),
                    nombre_completo=user_metadata.get("nombre_completo", ""),
                    empresa=user_metadata.get("empresa", ""),
                    telefono=user_metadata.get("telefono", ""),
                )
                logger.info("Cliente auto-creado en BD con metadata: %s", cliente_id)
                # -----------------------------------------------------
                
            request.auth_payload = payload
            return cliente
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT de Supabase expirado")
            raise HttpError(401, "El token ha expirado")
        except jwt.InvalidSignatureError:
            logger.warning("JWT de Supabase con firma invalida")
            raise HttpError(401, "Token inválido")
        except jwt.InvalidAudienceError:
            logger.warning("JWT de Supabase con audience invalido")
            raise HttpError(401, "Token inválido")
        except jwt.exceptions.MissingCryptographyError:
            logger.exception("Dependencia cryptography no disponible para validar JWT ES256")
            raise HttpError(500, "Error de configuracion del servidor de autenticacion")
        except jwt.InvalidTokenError:
            logger.warning("JWT de Supabase invalido")
            raise HttpError(401, "Token inválido")


class SupabaseAuthRegistro(HttpBearer):
    def authenticate(self, request, token):
        try:
            _log_auth_request(request, token)
            payload = _decode_supabase_token(token)
            request.auth_payload = payload
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT de registro expirado")
            raise HttpError(401, "El token ha expirado")
        except jwt.InvalidSignatureError:
            logger.warning("JWT de registro con firma invalida")
            raise HttpError(401, "Token inválido")
        except jwt.InvalidAudienceError:
            logger.warning("JWT de registro con audience invalido")
            raise HttpError(401, "Token inválido")
        except jwt.exceptions.MissingCryptographyError:
            logger.exception("Dependencia cryptography no disponible para validar JWT ES256")
            raise HttpError(500, "Error de configuracion del servidor de autenticacion")
        except jwt.InvalidTokenError:
            logger.warning("JWT de registro invalido")
            raise HttpError(401, "Token inválido")


class AdminAuth(SupabaseAuth):
    def authenticate(self, request, token):
        cliente = super().authenticate(request, token)
        if not cliente.es_admin:
            raise HttpError(403, "Acceso denegado. Se requieren permisos de administrador.")
        return cliente

# Instanciamos la clase para usarla en nuestros routers
auth_supabase = SupabaseAuth()
auth_admin = AdminAuth()
auth_registro = SupabaseAuthRegistro()