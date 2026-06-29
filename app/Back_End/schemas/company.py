import re
from pydantic import BaseModel, field_validator


class AdminInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

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
    company_name: str
    admin: AdminInfo


class RegistrationResponse(BaseModel):
    message: str
    email: str


class VerificationResponse(BaseModel):
    message: str
    company_name: str
    admin_email: str
