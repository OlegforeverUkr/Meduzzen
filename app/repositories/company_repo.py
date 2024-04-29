from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Company, User
from app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema
import logging
from app.services.handlers_errors import get_company_or_404
from app.utils.helpers import check_company_name_exist
from app.utils.visability import VisibilityEnum

logger = logging.getLogger("uvicorn")


class CompanyRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_companies(self, skip: int = 0, limit: int = 10,):
        query = (
            select(Company)
            .options(joinedload(Company.owner))
            .filter(Company.visibility == VisibilityEnum.PUBLIC)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_company(self, company_id: int, current_user: User):
        company = await get_company_or_404(session=self.session, id=company_id)
        if company.visibility == 'PRIVATE' and company.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="You are not the owner of this company")
        return company



    async def create_company(self, company: CompanyCreateSchema, current_user: User):
        await check_company_name_exist(session=self.session, company_name=company.company_name)

        db_company = Company(company_name=company.company_name,
                             description=company.description,
                             visibility=VisibilityEnum(company.visibility),
                             owner_id=current_user.id)
        self.session.add(db_company)
        await self.session.commit()
        await self.session.refresh(db_company)
        logger.info(f"Company created with ID: {db_company.id}")
        return db_company



    async def update_company(self, company_id: int, company: CompanyUpdateSchema):
        db_company = await get_company_or_404(session=self.session, id=company_id)

        if db_company:
            updated_values = company.dict(exclude_unset=True)
            for field, value in updated_values.items():
                if field == 'visibility':
                    value = VisibilityEnum(value)
                setattr(db_company, field, value)

            await self.session.commit()
            await self.session.refresh(db_company)
            logger.info(f"Company with ID: {db_company.id} is updated")
            return db_company
        else:
            raise HTTPException(status_code=404, detail="Company not found")


    async def delete_company(self, company_id: int):
        db_company = await get_company_or_404(session=self.session, id=company_id)

        if db_company:
            await self.session.delete(db_company)
            await self.session.commit()
            logger.info(f"Company is deleted")
        else:
            raise HTTPException(status_code=404, detail="Company not found")
