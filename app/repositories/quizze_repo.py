from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.db.models import Quiz, Question, Option
from app.schemas.quizzes import QuizUpdateSchema, QuizCreateSchema, QuizBaseSchema, QuestionBaseSchema, OptionBaseSchema
from app.services.handlers_errors import validate_quiz_data


class QuizRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_quiz(self, company_id: int, quiz_data: QuizCreateSchema):
        await validate_quiz_data(quiz_data)
        title = quiz_data.title
        description = quiz_data.description
        frequency_days = quiz_data.frequency_days
        new_quiz = Quiz(title=title, description= description, frequency_days=frequency_days, company_id=company_id)
        self.session.add(new_quiz)
        await self.session.flush()
        questions = []
        options = []

        for question_data in quiz_data.questions:
            text = question_data.text
            question = Question(text=text, quiz_id=new_quiz.id)
            self.session.add(question)
            await self.session.flush()
            questions.append(question)

            for option_data in question_data.options:
                text = option_data.text
                is_correct = option_data.is_correct
                option = Option(text=text, is_correct=is_correct, question_id=question.id)
                options.append(option)
                self.session.add(option)

        await self.session.commit()
        questions_data = [
            QuestionBaseSchema(
                text=question.text,
                options=[
                    OptionBaseSchema(
                        text=option.text,
                        is_correct=option.is_correct
                    ) for option in options
                ]
            ) for question in questions
        ]

        answer = QuizBaseSchema(title=new_quiz.title,
                                description=new_quiz.description,
                                frequency_days=new_quiz.frequency_days,
                                questions=questions_data)
        return answer


    async def get_quizzes_for_company(self, company_id: int, skip: int = 0, limit: int = 10):
        query = (
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        quizzes = result.scalars().all()
        return quizzes


    async def update_quiz(self, quiz_id: int, quiz_data: QuizUpdateSchema):
        quiz = (
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == quiz_id)
        )
        quiz_result = await self.session.execute(quiz)
        quiz = quiz_result.scalar_one_or_none()
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        try:
            quiz_data_dict = quiz_data.dict(exclude_unset=True)
            for field, value in quiz_data_dict.items():
                setattr(quiz, field, value)
            await self.session.commit()
            return quiz
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Validation quiz error: {e}")


    async def delete_quiz(self, quiz_id: int):
        quiz = await self.session.get(Quiz, quiz_id)
        if not quiz:
            return False
        await self.session.delete(quiz)
        await self.session.commit()
        return True
