from typing import List

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.db.models import Quiz, Question, Option
from app.schemas.quizzes import QuizUpdateSchema, QuizCreateSchema, QuizBaseSchema, QuestionBaseSchema, \
    OptionBaseSchema, QuestionUpdateSchema
from app.services.handlers_errors import validate_quiz_data
from app.utils.checking_uniqueness_quiz import checking_the_quiz_uniqueness
from app.utils.send_notification_after_create_quiz import send_notifications


class QuizRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_quiz(self, company_id: int, quiz_data: QuizCreateSchema):
        await validate_quiz_data(quiz_data)
        await checking_the_quiz_uniqueness(session=self.session, company_id=company_id, quiz_title=quiz_data.title)
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
        await send_notifications(session=self.session, quiz=new_quiz)
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


    async def update_questions(self, quiz_id: int, question_data_list: List[QuestionUpdateSchema]):
        quiz = (
            select(Quiz)
            .options(selectinload(Quiz.questions).selectinload(Question.options))
            .where(Quiz.id == quiz_id)
        )
        quiz_result = await self.session.execute(quiz)
        quiz = quiz_result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        try:
            for question_data in question_data_list:
                if not question_data.options and not question_data.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Not transferred ID question or options for create new question")

                if not question_data.id:
                    new_question = Question(text=question_data.text, quiz_id=quiz.id)
                    self.session.add(new_question)

                    for option_data in question_data.options:
                        new_option = Option(text=option_data.text, is_correct=option_data.is_correct,
                                            question_id=new_question.id)
                        self.session.add(new_option)
                else:
                    question = next((q for q in quiz.questions if q.id == question_data.id), None)
                    if question:
                        question.text = question_data.text

                        if question_data.options:
                            for option_data in question_data.options:
                                if option_data.id:
                                    option = next((o for o in question.options if o.id == option_data.id), None)
                                    if option:
                                        option.text = option_data.text
                                        option.is_correct = option_data.is_correct
                                    else:
                                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                                            detail=f"Option with ID {option_data.id} not found")
                                else:
                                    new_option = Option(text=option_data.text, is_correct=option_data.is_correct,
                                                        question_id=question.id)
                                    self.session.add(new_option)
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                            detail=f"Question with ID {question_data.id} not found")
            await self.session.commit()
            return quiz
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Validation error: {e}")


    async def delete_quiz(self, quiz_id: int):
        quiz = await self.session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        await self.session.delete(quiz)
        await self.session.commit()
