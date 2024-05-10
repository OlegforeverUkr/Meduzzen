from fastapi import HTTPException, status, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User, CompanyMember
from app.enums.roles_users import RoleEnum
from app.services.get_user_from_token import get_current_user_from_token


async def verify_user_permission(user_id: int, current_user: User = Depends(get_current_user_from_token)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )


async def verify_company_permissions(company_id: int,
                                     session: AsyncSession = Depends(get_session),
                                     current_user: User = Depends(get_current_user_from_token)):
    result = await session.execute(
        select(CompanyMember).filter(CompanyMember.company_id == company_id)
    )

    company_member = result.scalars().first()

    if company_member.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )



async def verify_company_owner(session: AsyncSession = Depends(get_session),
                               current_user: User = Depends(get_current_user_from_token)):
    result = await session.execute(
        select(CompanyMember).filter(
            CompanyMember.user_id == current_user.id,
            CompanyMember.role == RoleEnum.OWNER,
        )
    )

    company_member = result.scalar_one_or_none()

    if not company_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this company",
        )



async def verify_company_owner_or_admin(session: AsyncSession = Depends(get_session),
                                        current_user: User = Depends(get_current_user_from_token)):
    result = await session.execute(
        select(CompanyMember).filter(
            (CompanyMember.user_id == current_user.id) &
            ((CompanyMember.role == RoleEnum.OWNER) | (CompanyMember.role == RoleEnum.ADMIN))
        )
    )

    company_member = result.scalar_one_or_none()

    if not company_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner or admin of this company",
        )