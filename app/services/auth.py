from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.services.password_hash import PasswordHasher
from app.utils.helpers import get_user_by_username


async def authenticate_user(username: str, password: str, session: AsyncSession):
    user = await get_user_by_username(session=session, username=username)
    if not user or not PasswordHasher.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return user