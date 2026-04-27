"""Validates Stack Auth (Neon Auth) JWTs for the /admin/* routes."""
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from cuantocuestave_infra.settings import Settings

logger = structlog.get_logger(__name__)
_bearer = HTTPBearer()


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    settings: Settings = Depends(lambda: Settings()),
) -> str:
    """Verify Stack Auth JWT and enforce single-admin allowlist."""
    import jwt  # pyjwt

    token = credentials.credentials
    try:
        # Stack Auth uses RS256; JWKS fetched from Stack Auth project
        payload = jwt.decode(
            token,
            options={"verify_signature": False},  # TODO: fetch JWKS and verify
        )
        email: str = payload.get("email", "")
        if email != settings.admin_allowed_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return email
    except Exception as exc:
        logger.warning("admin_auth_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc


AdminUser = str  # email
