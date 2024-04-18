from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.schemas.users import UserSchema, UserCreateSchema, UserUpdateRequestSchema
from app.repositories.user_repo import UserRepository

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@router.get(path="/users/", response_model=List[UserSchema], status_code=200)
async def get_all_users_router(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    users = await repo.get_users(skip=skip, limit=limit)
    return users


@router.get(path="/users/{user_id}", response_model=UserSchema, status_code=200)
async def get_user_router(user_id: int, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    user = await repo.get_user(user_id=user_id)
    return user


@router.post(path="/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user_router(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    new_user = await repo.create_user(user=user)
    return new_user


@router.patch(path="/users/{user_id}", response_model=UserSchema, status_code=200)
async def update_user_router(user_id: int, user: UserUpdateRequestSchema, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    updated_user = await repo.update_user(user_id=user_id, user=user)
    return updated_user



@router.delete(path="/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_router(user_id: int, session: AsyncSession = Depends(get_session)):
    await UserRepository(session=session).delete_user(user_id=user_id)
