from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskPriority
from app.schemas.user import UserRead


class TagRead(BaseModel):
    id: UUID
    name: str
    color: str
    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str
    parent_id: UUID | None = None


class CommentRead(BaseModel):
    id: UUID
    body: str
    author: UserRead
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assignee_id: UUID | None = None
    tag_names: list[str] = []


class TaskRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    order: int
    due_date: datetime | None
    project_id: UUID
    assignee: UserRead | None
    tags: list[TagRead]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assignee_id: UUID | None = None
    tag_names: list[str] | None = None


class TaskFilters(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: UUID | None = None
    search: str | None = None
    skip: int = 0
    limit: int = 50