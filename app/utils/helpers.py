import re

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import User


password_valid_regex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,}$')


async def check_user_by_username_exist(session: AsyncSession, username: str, user_id: int = None):
    existing_user = await session.execute(
        select(User).filter(User.username == username)
    )
    user = existing_user.scalar()
    if user:
        if not user_id or user.id != user_id:
            return user
    return None


async def check_user_by_email_exist(session: AsyncSession, email: str, user_id: int = None):
    existing_user = await session.execute(
        select(User).filter(User.email == email)
    )
    user = existing_user.scalar()
    if user:
        if not user_id or user.id != user_id:
            return user
    return None

