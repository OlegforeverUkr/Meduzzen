from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Quiz


async def checking_the_quiz_uniqueness(session: AsyncSession, quiz_title: str, company_id: int):
    query = (
        select(Quiz)
        .where(and_(Quiz.company_id == company_id, Quiz.title == quiz_title)))
    result = await session.execute(query)
    company_members = result.scalar_one_or_none()

    if company_members:
        raise HTTPException(status_code=400, detail="Quiz already exist!")