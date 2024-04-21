import re

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import User


password_valid_regex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,}$')


async def check_user_by_username_exist(session: AsyncSession, username: str, user_id: int = None) -> None:
    existing_user = await session.execute(
        select(User).filter(User.username == username)
    )
    user = existing_user.scalar()
    if user:
        if not user_id or user.id != user_id:
            raise HTTPException(status_code=409, detail="Username already exists")


async def check_user_by_email_exist(session: AsyncSession, email: str, user_id: int = None) -> None:
    existing_user = await session.execute(
        select(User).filter(User.email == email)
    )
    user = existing_user.scalar()
    if user:
        if not user_id or user.id != user_id:
            raise HTTPException(status_code=409, detail="Email already exists")


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    getting_user = await session.execute(
        select(User).filter(User.username == username)
    )
    user = getting_user.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



async def get_user_by_email(session: AsyncSession, user_email: str) -> User:
    getting_user = await session.execute(
        select(User).filter(User.email == user_email)
    )
    user = getting_user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user