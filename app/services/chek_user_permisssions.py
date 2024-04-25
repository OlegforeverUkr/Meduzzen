from fastapi import HTTPException, status

from app.db.models import User



async def verify_user_permission(user_id: int, current_user: User):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have rights to change data",
        )
