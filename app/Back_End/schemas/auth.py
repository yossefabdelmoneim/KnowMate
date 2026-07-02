from datetime import datetime
from typing import Optional
import uuid # Import uuid

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: str = Field(..., description="User email address", example="user@example.com")
    password: str = Field(..., description="User password", example="SecurePass123!")
    full_name: Optional[str] = Field(None, description="User full name", example="John Doe")
    role: Optional[str] = Field("employee", description="User role", example="employee")
    company_id: Optional[int] = Field(None, description="Company ID")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "role": "employee",
                "company_id": None
            }
        }


class UserOut(BaseModel):
    id: uuid.UUID = Field(..., description="User ID") # Changed from int to uuid.UUID
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    # company_id: Optional[int] = Field(None, description="Associated company ID") # Removed company_id
    role: str = Field(..., description="User role (employee, manager, admin, COMPANY_ADMIN)")
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "f7d63629-fdd0-4f3f-836a-3c4e31ebaef1", # Example updated to UUID
                "email": "user@example.com",
                "full_name": "John Doe",
                # "company_id": 1, # Removed company_id
                "role": "employee",
                "created_at": "2026-06-30T01:00:53.492877+03:00"
            }
        }


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RoleUpdate(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID to update") # Changed from int to uuid.UUID
    role: str = Field(..., description="New role (employee, manager, admin, COMPANY_ADMIN)", example="manager")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "f7d63629-fdd0-4f3f-836a-3c4e31ebaef1", # Example updated to UUID
                "role": "manager"
            }
        }

    # Optional for compatibility with both projects.
    expires_in: int | None = None


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="User email address", example="user@example.com")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token from email link")
    password: str = Field(..., description="New password", example="NewSecurePass123!")