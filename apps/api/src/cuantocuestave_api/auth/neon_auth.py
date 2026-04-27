"""Validates Neon Auth (better-auth) JWTs for /admin/* routes."""
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from cuantocuestave_infra.settings import Settings

logger = structlog.get_logger(__name__)
_bearer = HTTPBearer()

_jwks_client = None


def _get_jwks_client(neon_auth_url: str):
    import jwt  # pyjwt

    global _jwks_client
    if _jwks_client is None:
        jwks_uri = f"{neon_auth_url.rstrip('/')}/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_uri, cache_keys=True)
    return _jwks_client


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    settings: Settings = Depends(lambda: Settings()),
) -> str:
    """Verify Neon Auth JWT and enforce single-admin allowlist."""
    import jwt  # pyjwt

    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client(settings.neon_auth_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        email: str = payload.get("email", "")
        if email != settings.admin_allowed_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return email
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("admin_auth_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc


AdminUser = str  # email
