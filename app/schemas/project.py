from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.project import ProjectRole
from app.schemas.user import UserRead


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class ProjectRead(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    owner_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectMemberRead(BaseModel):
    user: UserRead
    role: ProjectRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    user_id: UUID
    role: ProjectRole = ProjectRole.member