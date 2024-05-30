from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Quiz, QuizResult


async def check_timeout(session: AsyncSession, quiz: Quiz, user_id: int):
    existing_result = await session.execute(select(QuizResult)
                                            .filter((QuizResult.quiz_id == quiz.id) & (QuizResult.user_id == user_id)))
    existing_result = existing_result.scalar_one_or_none()

    if existing_result:
        time_difference = datetime.utcnow() - existing_result.solved_at
        frequency_days = quiz.frequency_days
        if time_difference.days < frequency_days:
            raise HTTPException(status_code=403, detail="Not enough time has passed since the last attempt")
