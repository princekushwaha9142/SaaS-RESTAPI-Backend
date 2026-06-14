import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.project import Project, ProjectMember, ProjectRole
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[\s_-]+", "-", slug).strip("-")


async def get_project(db: AsyncSession, project_id: UUID, user: User) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members).selectinload(ProjectMember.user))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    member_ids = {m.user_id for m in project.members} | {project.owner_id}
    if user.id not in member_ids:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    return project


async def list_projects(db: AsyncSession, user: User) -> list[Project]:
    result = await db.execute(
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id, isouter=True)
        .where(
            (Project.owner_id == user.id) | (ProjectMember.user_id == user.id)
        )
        .distinct()
    )
    return list(result.scalars().all())


async def create_project(db: AsyncSession, data: ProjectCreate, owner: User) -> Project:
    base_slug = _slugify(data.name)
    slug = base_slug
    counter = 1
    while True:
        exists = await db.execute(select(Project).where(Project.slug == slug))
        if not exists.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    project = Project(name=data.name, slug=slug, description=data.description, owner_id=owner.id)
    db.add(project)
    await db.flush()

    owner_membership = ProjectMember(project_id=project.id, user_id=owner.id, role=ProjectRole.owner)
    db.add(owner_membership)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(db: AsyncSession, project: Project, data: ProjectUpdate, user: User) -> Project:
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can update it")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project, user: User) -> None:
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can delete it")
    await db.delete(project)
    await db.commit()


async def add_member(db: AsyncSession, project: Project, user_id: UUID, role: ProjectRole, actor: User) -> ProjectMember:
    if project.owner_id != actor.id:
        raise HTTPException(status_code=403, detail="Only the project owner can add members")
    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User is already a member")
    membership = ProjectMember(project_id=project.id, user_id=user_id, role=role)
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def remove_member(db: AsyncSession, project: Project, user_id: UUID, actor: User) -> None:
    if project.owner_id != actor.id:
        raise HTTPException(status_code=403, detail="Only the project owner can remove members")
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(membership)
    await db.commit()