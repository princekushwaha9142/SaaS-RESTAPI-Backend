from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.task import Task, Comment, Tag
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilters, CommentCreate


async def _assert_project_member(db: AsyncSession, project_id: UUID, user: User) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        membership = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user.id,
            )
        )
        if not membership.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not a project member")


async def _resolve_tags(db: AsyncSession, tag_names: list[str]) -> list[Tag]:
    tags = []
    for name in tag_names:
        result = await db.execute(select(Tag).where(Tag.name == name.lower()))
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=name.lower())
            db.add(tag)
            await db.flush()
        tags.append(tag)
    return tags


def _task_query():
    return (
        select(Task)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.tags),
        )
    )


async def list_tasks(db: AsyncSession, project_id: UUID, filters: TaskFilters, user: User) -> list[Task]:
    await _assert_project_member(db, project_id, user)
    q = _task_query().where(Task.project_id == project_id)
    if filters.status:
        q = q.where(Task.status == filters.status)
    if filters.priority:
        q = q.where(Task.priority == filters.priority)
    if filters.assignee_id:
        q = q.where(Task.assignee_id == filters.assignee_id)
    if filters.search:
        term = f"%{filters.search}%"
        q = q.where(or_(Task.title.ilike(term), Task.description.ilike(term)))
    q = q.order_by(Task.order, Task.created_at).offset(filters.skip).limit(filters.limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: UUID, user: User) -> Task:
    result = await db.execute(_task_query().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await _assert_project_member(db, task.project_id, user)
    return task


async def create_task(db: AsyncSession, project_id: UUID, data: TaskCreate, creator: User) -> Task:
    await _assert_project_member(db, project_id, creator)
    tags = await _resolve_tags(db, data.tag_names)
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        project_id=project_id,
        creator_id=creator.id,
        assignee_id=data.assignee_id,
        tags=tags,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return await get_task(db, task.id, creator)


async def update_task(db: AsyncSession, task_id: UUID, data: TaskUpdate, user: User) -> Task:
    task = await get_task(db, task_id, user)
    update_data = data.model_dump(exclude_none=True, exclude={"tag_names"})
    for field, value in update_data.items():
        setattr(task, field, value)
    if data.tag_names is not None:
        task.tags = await _resolve_tags(db, data.tag_names)
    await db.commit()
    return await get_task(db, task_id, user)


async def delete_task(db: AsyncSession, task_id: UUID, user: User) -> None:
    task = await get_task(db, task_id, user)
    await db.delete(task)
    await db.commit()


async def add_comment(db: AsyncSession, task_id: UUID, data: CommentCreate, author: User) -> Comment:
    task = await get_task(db, task_id, author)
    comment = Comment(body=data.body, task_id=task.id, author_id=author.id, parent_id=data.parent_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment.id)
    )
    return result.scalar_one()


async def list_comments(db: AsyncSession, task_id: UUID, user: User) -> list[Comment]:
    task = await get_task(db, task_id, user)
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.task_id == task.id, Comment.parent_id == None)
        .order_by(Comment.created_at)
    )
    return list(result.scalars().all())