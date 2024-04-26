from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User
from app.services.get_user_from_token import get_current_user_from_token
from app.services.handlers_errors import get_company_or_404


async def verify_user_permission(user_id: int, current_user: User = Depends(get_current_user_from_token)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )


async def verify_company_permissions(company_id: int,
                                     session: AsyncSession = Depends(get_session),
                                     current_user: User = Depends(get_current_user_from_token)):
    company = await get_company_or_404(session=session, id=company_id)
    if company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )