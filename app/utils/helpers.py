import re

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, Company

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


async def check_company_name_exist(session: AsyncSession, company_name: str):
    query = select(Company).where(Company.company_name == company_name)
    result = await session.execute(query)
    company = result.scalars().first()
    if company:
        raise HTTPException(status_code=400, detail="Company with this name already exists")
