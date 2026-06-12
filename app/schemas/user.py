from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None