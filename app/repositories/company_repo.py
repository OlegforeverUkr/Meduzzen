from sqlalchemy.exc import DatabaseError
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from app.db.models import Company, User
from app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema
import logging
from app.services.handlers_errors import get_company_or_404

logger = logging.getLogger("uvicorn")


class CompanyRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_companies(self, skip: int = 0, limit: int = 10,):
        query = (
            select(Company)
            .options(joinedload(Company.owner))
            .filter(Company.visibility == "public")
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_company(self, company_id: int):
        try:
            result = await get_company_or_404(session=self.session, id=company_id)
            return result
        except DatabaseError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")


    async def create_company(self, company: CompanyCreateSchema, current_user: User):
        try:
            db_company = Company(company_name=company.company_name,
                                 description=company.description,
                                 visibility=company.visibility,
                                 owner_id=current_user.id)
            self.session.add(db_company)
            await self.session.commit()
            await self.session.refresh(db_company)
            logger.info(f"Company created with ID: {db_company.id}, owner: {current_user.id}")
            return db_company
        except DatabaseError as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def update_company(self, company_id: int, company: CompanyUpdateSchema):
        db_company = await get_company_or_404(session=self.session, id=company_id)
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        if db_company:
            updated_values = company.dict(exclude_unset=True)
            for field, value in updated_values.items():
                setattr(db_company, field, value)

            await self.session.commit()
            await self.session.refresh(db_company)
            logger.info(f"Company with ID: {db_company.id} is updated")
            return db_company
        else:
            raise HTTPException(status_code=404, detail="Company not found")


    async def delete_company(self, company_id: int):
        db_company = await get_company_or_404(session=self.session, id=company_id)
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        if db_company:
            await self.session.delete(db_company)
            await self.session.commit()
            logger.info(f"Company is deleted")
        else:
            raise HTTPException(status_code=404, detail="Company not found")
