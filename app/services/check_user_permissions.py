from fastapi import HTTPException, status, Depends
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User, CompanyMember, Quiz
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
    result = await session.execute(select(CompanyMember).filter((CompanyMember.company_id == company_id) &
                                                                (CompanyMember.user_id == current_user.id)))
    company_member = result.scalars().first()

    if not company_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found company",
        )
    
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



async def verify_company_owner_or_admin(company_id: int,
                                        session: AsyncSession = Depends(get_session),
                                        current_user: User = Depends(get_current_user_from_token)):
    result = await session.execute(
        select(CompanyMember).filter(
            (CompanyMember.user_id == current_user.id) &
            (CompanyMember.company_id == company_id) &
            ((CompanyMember.role == RoleEnum.OWNER) | (CompanyMember.role == RoleEnum.ADMIN))
        )
    )

    company_member = result.scalars().first()

    if not company_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner or admin of this company",
        )


async def verify_quiz_permissions(quiz_id: int,
                                  session: AsyncSession = Depends(get_session),
                                  current_user: User = Depends(get_current_user_from_token)):
    result = await session.execute(select(Quiz).filter(Quiz.id == quiz_id))
    quiz = result.scalars().first()

    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    result = await session.execute(
        select(CompanyMember).filter(
              and_(
                  CompanyMember.company_id == quiz.company_id,
                  CompanyMember.user_id == current_user.id
              )
        )
    )
    company_member = result.scalars().first()

    if not company_member or company_member.role not in [RoleEnum.ADMIN, RoleEnum.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this quiz's results.",
        )


