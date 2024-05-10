from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Company, User, CompanyMember
from app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema, CompanySchema
import logging

from app.services.company_services import CompanyServices
from app.services.handlers_errors import get_company_or_404
from app.utils.helpers import check_company_name_exist
from app.enums.roles_users import RoleEnum
from app.enums.visability import VisibilityEnum

logger = logging.getLogger("uvicorn")


class CompanyRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_companies(self, skip: int = 0, limit: int = 10):
        query = (
            select(Company, User.username)
            .join(Company.members)
            .join(User, User.id == CompanyMember.user_id)
            .filter(Company.visibility == VisibilityEnum.PUBLIC)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        companies_list = await CompanyServices.get_companies_from_query(result)
        return companies_list


    async def get_company(self, company_id: int, current_user: User):
        company = await get_company_or_404(session=self.session, id=company_id)

        company_member = await self.session.execute(
            select(CompanyMember)
            .filter(CompanyMember.company_id == company_id, CompanyMember.user_id == current_user.id)
        )

        if not company_member:
            raise HTTPException(status_code=404, detail="User not found")

        return CompanySchema(id=company.id,
                             company_name=company.company_name,
                             description=company.description,
                             visibility=company.visibility,
                             owner=current_user.username)



    async def create_company(self, company: CompanyCreateSchema, current_user: User):
        await check_company_name_exist(session=self.session, company_name=company.company_name)

        db_company = Company(company_name=company.company_name,
                             description=company.description,
                             visibility=VisibilityEnum(company.visibility))

        company_member = CompanyMember(user_id=current_user.id, role=RoleEnum.OWNER)
        db_company.members.append(company_member)

        self.session.add(db_company)
        await self.session.commit()
        await self.session.refresh(db_company)

        company_schema = CompanySchema(
            id=db_company.id,
            company_name=db_company.company_name,
            description=db_company.description,
            visibility=db_company.visibility,
            owner=current_user.username)
        logger.info(f"Company created with ID: {db_company.id}")
        return company_schema



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


    async def create_admin_for_company_repo(self, company_member_id: int):
        company_member = await self.session.get(CompanyMember, company_member_id)

        if company_member:
            company_member.role = RoleEnum.ADMIN
            await self.session.commit()
            new_admin = await self.session.get(User, company_member.user_id)
            return new_admin
        else:
            raise HTTPException(status_code=404, detail="Company or user not found")


    async def get_all_company_admins_repo(self, company_id: int):
        db_company = await get_company_or_404(session=self.session, id=company_id)

        if db_company:
            query = (
                select(User)
                .join(CompanyMember)
                .filter(
                    CompanyMember.company_id == company_id,
                    CompanyMember.role == RoleEnum.ADMIN
                )
            )
            result = await self.session.execute(query)
            admins = result.scalars().all()
            if not admins:
                raise HTTPException(status_code=404, detail="No admins found for the company")
            return admins
        else:
            raise HTTPException(status_code=404, detail="Company not found")


    async def get_all_company_members_repo(self, company_id: int):
        db_company = await get_company_or_404(session=self.session, id=company_id)

        if db_company:
            query = (
                select(User)
                .join(CompanyMember)
                .filter(
                    CompanyMember.company_id == company_id
                )
            )
            result = await self.session.execute(query)
            members = result.scalars().all()
            if not members:
                raise HTTPException(status_code=404, detail="No members found for the company")
            return members
        else:
            raise HTTPException(status_code=404, detail="Company not found")
