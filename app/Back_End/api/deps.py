"""Shared FastAPI dependencies: auth, DB session, current user.

Two parallel auth paths converge on a `current_user`:

1. JWT bearer  → `Authorization: Bearer <token>`  (web UI)
2. API key      → `X-API-Key: <plaintext>`          (programmatic clients)

Routes that accept EITHER use `get_current_user`. Routes that accept
only one use the specific dependency directly.

Implementation note: We register `HTTPBearer(auto_error=False)` as a
sub-dependency of `get_current_user` so FastAPI knows about the security
scheme — this is what makes Swagger UI render the 🔒 Authorize button
and the per-endpoint lock icons. The dependency itself returns None
when no Bearer header is present (auto_error=False), and we then fall
through to the X-API-Key check.
"""

from __future__ import annotations

import logging

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.Back_End.core.data_analysis.exceptions import (
    AuthenticationError, InvalidApiKeyError, InvalidTokenError, NotFoundError,
)
from app.Back_End.core.security import decode_access_token
from app.Back_End.db.session import get_db
from app.Back_End.db.models import User
from app.Back_End.services.data_analysis.api_key_service import ApiKeyService
from app.Back_End.services.data_analysis.auth_service import AuthService

logger = logging.getLogger(__name__)

# Register the bearer scheme ONCE at import time. `auto_error=False` means
# the dependency returns None instead of raising when no Bearer header is
# present — letting `get_current_user` fall through to the API-key path.
# This is also what tells FastAPI's OpenAPI generator to register the
# `bearerAuth` security scheme, which is what makes Swagger show the
# Authorize button.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user via EITHER JWT bearer OR X-API-Key.

    Decision order:
    1. If `X-API-Key` header is present, validate it. Raise on failure.
    2. Else if `Authorization: Bearer <token>` is present, validate it. Raise on failure.
    3. Else raise AuthenticationError (no credentials provided).

    This deliberately does NOT fall back from one path to the other —
    if you sent an API key and it's invalid, you get a 401, not a
    silent attempt to read a JWT you didn't send.
    """
    # 1. Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return ApiKeyService(db).validate_key(api_key)

    # 2. Try JWT bearer (credentials comes from the HTTPBearer sub-dependency)
    if credentials is not None and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        try:
            payload = decode_access_token(token)
        except ValueError as exc:
            raise InvalidTokenError(f"Invalid token: {exc}") from exc

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidTokenError("Token payload missing 'sub'.")

        try:
            user_id = int(user_id_str)
        except ValueError as exc:
            raise InvalidTokenError("Token 'sub' is not a valid integer.") from exc

        user = AuthService(db).get_user(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    # 3. No credentials provided
    raise AuthenticationError(
        "No credentials provided. Send either Authorization: Bearer <jwt> "
        "or X-API-Key: <key>."
    )


# --- Path-specific dependencies (for routes that only accept ONE path) -----

def get_current_user_from_jwt(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Strict JWT-only auth — used by API key management routes."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidTokenError(
            "Missing or malformed Authorization header. Expected: Bearer <token>."
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise InvalidTokenError(f"Invalid token: {exc}") from exc

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidTokenError("Token payload missing 'sub'.")

    try:
        user_id = int(user_id_str)
    except ValueError as exc:
        raise InvalidTokenError("Token 'sub' is not a valid integer.") from exc

    user = AuthService(db).get_user(user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user


def get_current_user_from_api_key(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Strict API-key-only auth."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise InvalidApiKeyError("Missing X-API-Key header.")
    return ApiKeyService(db).validate_key(api_key)
