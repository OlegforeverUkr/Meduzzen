from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models import Quiz, QuizResult


async def check_timeout(session: AsyncSession, quiz: Quiz, user_id: int):
    existing_result = await session.execute(select(QuizResult)
                                            .filter((QuizResult.quiz_id == quiz.id) & (QuizResult.user_id == user_id)))
    existing_result = existing_result.scalar_one_or_none()

    if existing_result:
        time_difference = datetime.utcnow() - existing_result.solved_at
        frequency_days = quiz.frequency_days
        if time_difference.days < frequency_days:
            raise ValueError("Not enough time has passed since the last attempt")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")