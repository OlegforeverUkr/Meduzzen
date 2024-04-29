from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.models import User, Company


async def get_user_or_404(session, **kwargs):
    query = select(User).where(User.id == kwargs.get('id'))
    result = await session.execute(query)
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="User not found")
    return instance



async def get_company_or_404(session, **kwargs):
    query = select(Company).where(Company.id == kwargs.get('id'))
    result = await session.execute(query)
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="Company not found")
    return instance
