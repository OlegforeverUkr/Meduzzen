from fastapi import HTTPException, status, Depends

from app.db.models import User
from app.services.get_user_from_token import get_current_user_from_token


async def verify_user_permission(user_id: int, current_user: User = Depends(get_current_user_from_token)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )
