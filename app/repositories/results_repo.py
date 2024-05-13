from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.db.models import Quiz, QuizResult
from app.schemas.result_quizes import QuizResultSchema, QuizAttemptSchema
from app.services.results_for_quiz import calculate_quiz_score
from app.utils.check_time_solve_quiz import check_timeout


class ResultsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_quiz_for_solve_repo(self, quiz_id: int):
        quiz = (
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == quiz_id)
        )
        quiz_result = await self.session.execute(quiz)
        quiz = quiz_result.scalar_one_or_none()
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        return quiz


    async def calculate_and_save_quiz_result(self, user_id: int, quiz_attempt: QuizAttemptSchema, company_id: int):
        quiz = await self.get_quiz_for_solve_repo(quiz_id=quiz_attempt.quiz_id)
        await check_timeout(self.session, quiz, user_id)
        score = calculate_quiz_score(quiz, quiz_attempt.answers)

        total_correct_answers = sum(1 for answer in quiz_attempt.answers if answer.is_correct)
        total_questions_answered = len(quiz.questions)

        quiz_result = QuizResult(user_id=user_id,
                                 quiz_id=quiz_attempt.quiz_id,
                                 company_id=company_id,
                                 score=score,
                                 total_correct_answers=total_correct_answers,
                                 total_questions_answered=total_questions_answered)
        self.session.add(quiz_result)
        await self.session.commit()

        return QuizResultSchema(user_id=quiz_result.user_id,
                                quiz_id=quiz_result.quiz_id,
                                company_id=quiz_result.company_id,
                                score=quiz_result.score)


    async def get_quiz_average_score(self, quiz_id: int):
        quiz_results = (select(QuizResult)
                        .where(QuizResult.quiz_id == quiz_id))

        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()

        if quiz_results:
            total_questions_answered = 0
            total_correct_answers = 0

            for result in quiz_results:
                total_questions_answered += result.total_questions_answered
                total_correct_answers += result.total_correct_answers

            if total_questions_answered == 0:
                return None

            average_score = total_correct_answers / total_questions_answered
            return average_score
        else:
            raise HTTPException(status_code=404, detail="No quiz results found")


    async def get_user_average_score(self, user_id: int):
        quiz_results = (select(QuizResult)
                        .where(QuizResult.user_id == user_id))

        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()

        if quiz_results:
            total_questions_answered = 0
            total_correct_answers = 0

            for result in quiz_results:
                total_questions_answered += result.total_questions_answered
                total_correct_answers += result.total_correct_answers

            if total_questions_answered == 0:
                return None

            average_score = total_correct_answers / total_questions_answered
            return average_score
        else:
            raise HTTPException(status_code=404, detail="No quiz results found")


    async def get_company_average_score(self, company_id: int):
        quiz_results = (select(QuizResult)
                        .where(QuizResult.company_id == company_id))

        quiz_results = await self.session.execute(quiz_results)
        quiz_results = quiz_results.scalars().all()

        if quiz_results:
            total_questions_answered = 0
            total_correct_answers = 0

            for result in quiz_results:
                total_questions_answered += result.total_questions_answered
                total_correct_answers += result.total_correct_answers

            if total_questions_answered == 0:
                return None

            average_score = total_correct_answers / total_questions_answered
            return average_score
        else:
            raise HTTPException(status_code=404, detail="No quiz results found")
