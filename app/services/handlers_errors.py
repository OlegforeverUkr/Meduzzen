from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select

from app.db.models import User, Company
from app.schemas.quizzes import QuizCreateSchema


async def get_user_or_404(session, **kwargs):
    query = select(User).where(User.id == kwargs.get('id'))
    result = await session.execute(query)
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="User not found")
    return instance



async def get_company_or_404(session, **kwargs):
    if kwargs.get("id"):
        query = select(Company).where(Company.id == kwargs.get('id'))
        result = await session.execute(query)
        instance = result.scalars().first()
    else:
        query = select(Company).where(Company.company_name == kwargs.get('company_name'))
        result = await session.execute(query)
        instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="Company not found")
    return instance


async def validate_quiz_data(quiz_data: QuizCreateSchema):
    try:
        QuizCreateSchema(**quiz_data.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation quiz error: {e}")