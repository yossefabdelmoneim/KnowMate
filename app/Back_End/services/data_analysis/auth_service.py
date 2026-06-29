"""AuthService — register, login, JWT issuance."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from KnowMate.app.Back_End.core.config import settings
from KnowMate.app.Back_End.core.data_analysis.exceptions import InvalidCredentialsError, ValidationError
from KnowMate.app.Back_End.core.security import create_access_token, hash_password, verify_password
from KnowMate.app.Back_End.models.data_analysis.user import User
from KnowMate.app.Back_End.repositories.data_analysis.user_repository import UserRepository
from KnowMate.app.Back_End.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic

logger = logging.getLogger(__name__)


class AuthService:
    """User registration + login + JWT issuance."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def register(self, request: RegisterRequest) -> UserPublic:
        if self.repo.get_by_email(request.email):
            raise ValidationError("An account with this email already exists.")

        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
        )
        self.repo.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info("Registered user %s (id=%s)", user.email, user.id)
        return UserPublic.model_validate(user)

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(request.email)
        if user is None or not verify_password(request.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password.")
        if not user.is_active:
            raise InvalidCredentialsError("This account is disabled.")

        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_ttl_minutes * 60,
            user_id=user.id,
        )

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.repo.get_by_id(user_id)
