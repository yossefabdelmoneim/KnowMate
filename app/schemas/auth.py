from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
