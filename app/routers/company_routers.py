from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.company_repo import CompanyRepository
from app.schemas.company import CompanySchema, CompanyCreateSchema, CompanyUpdateSchema
from app.services.check_user_permissions import verify_company_permissions
from app.services.get_user_from_token import get_current_user_from_token

company_routers = APIRouter()


@company_routers.get(path="/companies/", response_model=List[CompanySchema])
async def list_companies_router(session: AsyncSession = Depends(get_session)):
    company_repo = CompanyRepository(session=session)
    companies = await company_repo.get_companies()
    return companies


@company_routers.get(path="/companies/{company_id}/", response_model=CompanySchema)
async def get_company_by_id(company_id: int, session: AsyncSession = Depends(get_session)):
    company_repo = CompanyRepository(session=session)
    company = await company_repo.get_company(company_id=company_id)
    return company



@company_routers.post(path="/companies/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(company_data: CompanyCreateSchema,
                         session: AsyncSession = Depends(get_session),
                         current_user: User = Depends(get_current_user_from_token)):
    company_repo = CompanyRepository(session=session)
    new_company = await company_repo.create_company(company=company_data, current_user=current_user)
    return CompanySchema(
        id=new_company.id,
        company_name=new_company.company_name,
        description=new_company.description,
        owner=new_company.owner,
        visibility=new_company.visibility
    )


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
    return CompanySchema(
        id=updated_company.id,
        company_name=updated_company.company_name,
        description=updated_company.description,
        owner=updated_company.owner,
        visibility=updated_company.visibility
    )


@company_routers.delete(path="/companies/{company_id}/",
                        status_code=status.HTTP_204_NO_CONTENT,
                        dependencies=[Depends(verify_company_permissions)])
async def delete_company(company_id: int, session: AsyncSession = Depends(get_session)):
    await CompanyRepository(session=session).delete_company(company_id=company_id)