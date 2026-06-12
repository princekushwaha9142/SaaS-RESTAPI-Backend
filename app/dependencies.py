from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import async_session_factory
from app.services.auth import decode_token
from app.services.user import get_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db():
    async with async_session_factory() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    token_data = decode_token(token, expected_type="access")
    user = await get_by_id(db, UUID(token_data.sub))
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user