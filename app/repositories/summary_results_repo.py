from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import QuizResult
from app.schemas.result_quizes import GeneralQuizResultSchema


class SummaryResultsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_user_quiz_results(self, user_id: int):
        quiz_results = (select(QuizResult).where(QuizResult.user_id == user_id))
        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()
        return [GeneralQuizResultSchema.from_orm(result) for result in quiz_results]


    async def get_company_user_results(self, company_id: int, user_id: int):
        quiz_results = (select(QuizResult).where(QuizResult.company_id == company_id, QuizResult.user_id == user_id))
        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()
        return [GeneralQuizResultSchema.from_orm(result) for result in quiz_results]


    async def get_company_all_user_results(self, company_id: int):
        quiz_results = (select(QuizResult).where(QuizResult.company_id == company_id))
        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()
        return [GeneralQuizResultSchema.from_orm(result) for result in quiz_results]


    async def get_company_quiz_results(self, company_id: int, quiz_id: int):
        quiz_results = (select(QuizResult).where(QuizResult.company_id == company_id, QuizResult.quiz_id == quiz_id))
        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()
        return [GeneralQuizResultSchema.from_orm(result) for result in quiz_results]
