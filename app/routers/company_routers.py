from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.company_repo import CompanyRepository
from app.repositories.quizze_repo import QuizRepository
from app.schemas.company import CompanySchema, CompanyCreateSchema, CompanyUpdateSchema
from app.schemas.quizzes import QuizCreateSchema, QuizReadSchema, QuizUpdateSchema, QuizBaseSchema, QuestionUpdateSchema
from app.schemas.users import UserSchema
from app.services.check_user_permissions import verify_company_permissions, verify_company_owner, \
    verify_company_owner_or_admin
from app.services.get_user_from_token import get_current_user_from_token

company_routers = APIRouter()


@company_routers.get(path="/companies/", response_model=List[CompanySchema])
async def list_companies_router(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    company_repo = CompanyRepository(session=session)
    companies = await company_repo.get_companies(skip=skip, limit=limit)
    return companies


@company_routers.get(path="/companies/{company_id}/", response_model=CompanySchema)
async def get_company_by_id(company_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    company_repo = CompanyRepository(session=session)
    company = await company_repo.get_company(company_id=company_id, current_user=current_user)
    return company



@company_routers.post(path="/companies/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(company_data: CompanyCreateSchema,
                         session: AsyncSession = Depends(get_session),
                         current_user: User = Depends(get_current_user_from_token)):
    company_repo = CompanyRepository(session=session)
    new_company = await company_repo.create_company(company=company_data, current_user=current_user)
    return new_company


@company_routers.patch(path="/companies/{company_id}/",
                       response_model=CompanySchema,
                       dependencies=[Depends(verify_company_permissions)])
async def update_company(
    company_id: int,
    company_data: CompanyUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    company_repo = CompanyRepository(session=session)
    updated_company = await company_repo.update_company(company_id=company_id,
                                                  company=company_data)
    return updated_company


@company_routers.post(path="/companies/{company_member_id}/",
                       response_model=  UserSchema,
                       dependencies=[Depends(verify_company_owner)])
async def create_admin_for_company(company_member_id: int, session: AsyncSession = Depends(get_session)):
    new_admin = await CompanyRepository(session).create_admin_for_company_repo(company_member_id=company_member_id)
    return new_admin


@company_routers.get(path="/companies/{company_id}/admins", response_model=list[UserSchema],
                     dependencies=[Depends(verify_company_permissions)])
async def get_all_company_admins(company_id: int, session: AsyncSession = Depends(get_session)):
    all_admins = await CompanyRepository(session).get_all_company_admins_repo(company_id=company_id)
    return all_admins


@company_routers.get(path="/companies/{company_id}/members", response_model=list[UserSchema],
                     dependencies=[Depends(verify_company_permissions)])
async def get_all_company_members(company_id: int, session: AsyncSession = Depends(get_session)):
    all_admins = await CompanyRepository(session).get_all_company_members_repo(company_id=company_id)
    return all_admins


@company_routers.delete(path="/companies/{company_id}/",
                        status_code=status.HTTP_204_NO_CONTENT,
                        dependencies=[Depends(verify_company_permissions)])
async def delete_company(company_id: int, session: AsyncSession = Depends(get_session)):
    await CompanyRepository(session=session).delete_company(company_id=company_id)

# _____________________________________________________________________________________________________

@company_routers.post(path="/companies/{company_id}/quizzes/",
                      response_model=QuizBaseSchema,
                      status_code=status.HTTP_201_CREATED,
                      dependencies=[Depends(verify_company_owner_or_admin)])
async def create_quiz_for_company(
    company_id: int,
    quiz_data: QuizCreateSchema,
    session: AsyncSession = Depends(get_session)):
    quiz_repo = QuizRepository(session=session)
    new_quiz = await quiz_repo.create_quiz(company_id=company_id, quiz_data=quiz_data)
    return new_quiz


@company_routers.get(path="/companies/{company_id}/quizzes/",
                     response_model=list[QuizReadSchema],
                     dependencies=[Depends(verify_company_permissions)])
async def get_quizzes_for_company(
    company_id: int,
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    quiz_repo = QuizRepository(session=session)
    quizzes = await quiz_repo.get_quizzes_for_company(company_id=company_id, skip=skip, limit=limit)
    return quizzes


@company_routers.patch(path="/companies/{company_id}/quizzes/{quiz_id}/",
                       response_model=QuizReadSchema,
                       dependencies=[Depends(verify_company_owner_or_admin)])
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    quiz_repo = QuizRepository(session=session)
    updated_quiz = await quiz_repo.update_quiz(quiz_id=quiz_id, quiz_data=quiz_data)
    return updated_quiz


@company_routers.patch(path="/companies/{company_id}/quizzes/{quiz_id}/update_questions",
                       response_model=QuizReadSchema,
                       dependencies=[Depends(verify_company_owner_or_admin)])
async def update_questions(
    quiz_id: int,
    questions_data: List[QuestionUpdateSchema],
    session: AsyncSession = Depends(get_session)
):
    quiz_repo = QuizRepository(session=session)
    updated_quiz = await quiz_repo.update_questions(quiz_id=quiz_id, question_data_list=questions_data)
    return updated_quiz


@company_routers.delete(path="/companies/{company_id}/quizzes/{quiz_id}/",
                        status_code=status.HTTP_204_NO_CONTENT,
                        dependencies=[Depends(verify_company_owner_or_admin)])
async def delete_quiz(quiz_id: int,
                      session: AsyncSession = Depends(get_session)):
    quiz_repo = QuizRepository(session=session)
    await quiz_repo.delete_quiz(quiz_id=quiz_id)
    return {"message": "Quiz was deleted" }
