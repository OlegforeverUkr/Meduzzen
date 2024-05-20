from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.summary_results_repo import SummaryResultsRepository
from app.schemas.result_quizes import GeneralQuizResultSchema
from app.services.check_user_permissions import verify_company_owner_or_admin
from app.services.get_user_from_token import get_current_user_from_token
from app.utils.csv_utils import generate_csv


total_results_router = APIRouter()


@total_results_router.get(path="/my-results/", response_model=List[GeneralQuizResultSchema])
async def get_my_total_results(current_user: User = Depends(get_current_user_from_token),
                         session: AsyncSession = Depends(get_session)):
    repository = SummaryResultsRepository(session)
    results = await repository.get_user_quiz_results(user_id=current_user.id)
    return results


@total_results_router.get(path="/company/{company_id}/user-total-results/{user_id}/",
                          response_model=List[GeneralQuizResultSchema],
                          dependencies=[Depends(verify_company_owner_or_admin)])
async def get_user_total_results(company_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    repository = SummaryResultsRepository(session)
    results = await repository.get_company_user_results(company_id=company_id, user_id=user_id)
    return results


@total_results_router.get(path="/company/{company_id}/all-users-total-results/",
                          response_model=List[GeneralQuizResultSchema],
                          dependencies=[Depends(verify_company_owner_or_admin)])
async def get_all_user_total_results(company_id: int, session: AsyncSession = Depends(get_session)):
    repository = SummaryResultsRepository(session)
    results = await repository.get_company_all_user_results(company_id=company_id)
    return results


@total_results_router.get(path="/company/{company_id}/quiz-total-results/{quiz_id}/",
                          response_model=List[GeneralQuizResultSchema],
                          dependencies=[Depends(verify_company_owner_or_admin)])
async def get_quiz_total_results(company_id: int, quiz_id: int, session: AsyncSession = Depends(get_session)):
    repository = SummaryResultsRepository(session)
    results = await repository.get_company_quiz_results(company_id=company_id, quiz_id=quiz_id)
    return results


@total_results_router.get(path="/company/{company_id}/export/quiz-results/{quiz_id}/csv",
                          dependencies=[Depends(verify_company_owner_or_admin)])
async def export_quiz_results_csv(company_id: int,
                                  quiz_id: int,
                                  session: AsyncSession = Depends(get_session)):
    repository = SummaryResultsRepository(session)
    results = await repository.get_company_quiz_results(company_id=company_id, quiz_id=quiz_id)

    file_path = rf"C:\Users\Oleg\Desktop\Results\quiz_results_for_company-{company_id}_quiz-{quiz_id}.csv"
    generate_csv(results, file_path)

    return FileResponse(path=file_path, media_type='text/csv', filename=f"quiz_results_{company_id}_{quiz_id}.csv")
