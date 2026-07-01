import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.Back_End.core.config import settings

# Use Argon2 instead of bcrypt
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


# ----------------------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    now = datetime.now(timezone.utc)

    payload = data.copy()
    payload.update(
        {
            "iat": now,
            "exp": now
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
    )

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )



def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def generate_verification_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(token.encode()).hexdigest()
    return token, hashed

def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

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