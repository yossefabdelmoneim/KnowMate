import re
from pydantic import BaseModel, field_validator, Field


class AdminInfo(BaseModel):
    first_name: str = Field(..., description="Admin's first name", example="John")
    last_name: str = Field(..., description="Admin's last name", example="Doe")
    email: str = Field(..., description="Admin's email address", example="admin@company.com")
    password: str = Field(
        ...,
        description="Admin's password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char)",
        example="SecurePass123!"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'`~/]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class CompanyRegistrationRequest(BaseModel):
    company_name: str = Field(..., description="Company name", example="Acme Corporation")
    admin: AdminInfo = Field(..., description="Admin user information")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corporation",
                "admin": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "admin@acme.com",
                    "password": "SecurePass123!"
                }
            }
        }


class RegistrationResponse(BaseModel):
    message: str = Field(..., description="Status message")
    email: str = Field(..., description="Admin email for verification")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Registration initiated. Please check your email to verify.",
                "email": "admin@acme.com"
            }
        }


class VerificationResponse(BaseModel):
    message: str = Field(..., description="Status message")
    company_name: str = Field(..., description="Verified company name")
    admin_email: str = Field(..., description="Admin email")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Company verified and created successfully. You can now log in.",
                "company_name": "Acme Corporation",
                "admin_email": "admin@acme.com"
            }
        }
