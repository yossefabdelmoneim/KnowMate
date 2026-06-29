from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from uuid import uuid4
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.Back_End.core.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------------------

def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# ----------------------------------------------------------------------
# JWT
# ----------------------------------------------------------------------

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Creates a JWT.

    Backward compatible with the existing project while adding useful
    claims (iat, jti, type).
    """
    to_encode = data.copy()

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update(
        {
            "iat": now,
            "exp": expire,
            "jti": uuid4().hex,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


# ----------------------------------------------------------------------
# API Keys
# ----------------------------------------------------------------------

def generate_api_key() -> tuple[str, str]:
    """
    Returns:
        (plaintext_key, hashed_key)

    Store only the hashed key in the database.
    Show the plaintext only once.
    """

    raw_secret = secrets.token_urlsafe(32)

    prefix = getattr(settings, "api_key_prefix", "sk-knowmate-")

    plaintext = f"{prefix}{raw_secret}"

    return plaintext, hash_api_key(plaintext)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def constant_time_eq(a: str, b: str) -> bool:
    return secrets.compare_digest(a, b)