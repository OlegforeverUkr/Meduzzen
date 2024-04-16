from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.schemas.users import UserSchema, UserCreateSchema, UserUpdateRequestSchema
from app.services.crud_users import get_users, get_user, create_user, update_user, delete_user

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@router.get(path="/users/", response_model=List[UserSchema])
async def get_all_users_router(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    users = await get_users(session, skip=skip, limit=limit)
    return users


@router.get(path="/users/{user_id}", response_model=UserSchema)
async def get_user_router(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post(path="/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user_router(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    try:
        new_user = await create_user(session, user=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_user


@router.put(path="/users/{user_id}", response_model=UserSchema)
async def update_user_router(user_id: int, user: UserUpdateRequestSchema, session: AsyncSession = Depends(get_session)):
    try:
        updated_user = await update_user(session, user_id=user_id, user=user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/users/{user_id}", response_model=UserSchema)
async def patch_user_router(user_id: int, user: UserUpdateRequestSchema, session: AsyncSession = Depends(get_session)):
    try:
        updated_user = await update_user(session, user_id, user)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(path="/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_router(user_id: int, session: AsyncSession = Depends(get_session)):
    try:
        await delete_user(session, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}