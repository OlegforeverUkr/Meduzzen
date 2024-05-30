from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.results_repo import ResultsRepository
from app.schemas.quizzes import QuizQuestionsSchema
from app.schemas.result_quizes import QuizAttemptSchema, QuizResultSchema
from app.services.check_user_permissions import verify_company_permissions, verify_quiz_permissions, \
    verify_company_owner_or_admin, verify_user_permission
from app.services.get_user_from_token import get_current_user_from_token


results_router = APIRouter(tags=["Results"])


@results_router.get(path="/{company_id}/{quiz_id}/",
                     response_model=QuizQuestionsSchema,
                     dependencies=[Depends(verify_company_permissions)])
async def get_quiz_for_solve(quiz_id: int,
                             session: AsyncSession = Depends(get_session)):
    repository = ResultsRepository(session)
    quiz = await repository.get_quiz_for_solve_repo(quiz_id=quiz_id)
    return quiz


@results_router.post(path="/{company_id}/quiz-attempt/",
                     response_model=QuizResultSchema,
                     dependencies=[Depends(verify_company_permissions)])
async def quiz_attempt(quiz_attempt: QuizAttemptSchema,
                       company_id: int,
                       session: AsyncSession = Depends(get_session),
                       current_user: User = Depends(get_current_user_from_token)):
    repository = ResultsRepository(session)
    answer = await repository.calculate_and_save_quiz_result(user_id=current_user.id,
                                                             quiz_attempt=quiz_attempt,
                                                             company_id=company_id)
    return answer



@results_router.get(path="/quiz-average-score/{quiz_id}",
                    response_model=float,
                    dependencies=[Depends(verify_quiz_permissions)])
async def quiz_average_score(quiz_id: int, session: AsyncSession = Depends(get_session)):
    repository = ResultsRepository(session)
    average_score = await repository.get_quiz_average_score(quiz_id)
    return average_score


@results_router.get(path="/user-average-score/{user_id}",
                    response_model=float,
                    dependencies=[Depends(verify_user_permission)])
async def user_average_score(user_id: int, session: AsyncSession = Depends(get_session)):
    repository = ResultsRepository(session)
    average_score = await repository.get_user_average_score(user_id)
    return average_score


@results_router.get(path="/company-average-score/{company_id}",
                    response_model=float,
                    dependencies=[Depends(verify_company_owner_or_admin)])
async def company_average_score(company_id: int, session: AsyncSession = Depends(get_session)):
    repository = ResultsRepository(session)
    average_score = await repository.get_company_average_score(company_id)
    return average_score
