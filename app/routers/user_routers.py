from typing import List

from fastapi import APIRouter, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.notification_repo import NotificationRepository
from app.schemas.notifications import NotificationSchema, NotificationReadSchema
from app.schemas.users import UserSchema, UserCreateSchema, UserUpdateRequestSchema, Token
from app.repositories.user_repo import UserRepository
from app.services.auth import authenticate_user
from app.services.check_user_permissions import verify_user_permission
from app.services.create_token import create_access_token
from app.services.get_user_from_token import get_current_user_from_token
from app.utils.token_verify import VerifyToken


user_router = APIRouter(tags=["Users"])

auth = VerifyToken()


@user_router.get("/")
def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@user_router.get(path="/users/", response_model=List[UserSchema], status_code=200)
async def get_all_users_router(skip: int = 0, limit: int = 10,
                               session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    users = await repo.get_users(skip=skip, limit=limit)
    return users


@user_router.get(path="/users/{user_id}", response_model=UserSchema, status_code=200)
async def get_user_router(user_id: int, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    user = await repo.get_user(user_id=user_id)
    return user


@user_router.post(path="/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user_router(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session=session)
    new_user = await repo.create_user(user=user)
    return new_user


@user_router.patch(path="/users/{user_id}", response_model=UserSchema, status_code=200, dependencies=[Depends(verify_user_permission)])
async def update_user_router(user: UserUpdateRequestSchema,
                             session: AsyncSession = Depends(get_session),
                             current_user: User = Depends(get_current_user_from_token)):
    repo = UserRepository(session=session)
    updated_user = await repo.update_user(user_id=current_user.id, user=user)
    return updated_user



@user_router.delete(path="/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_user_permission)])
async def delete_user_router(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    await UserRepository(session=session).delete_user(user_id=current_user.id)



@user_router.post(path="/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(form_data.username, form_data.password, session)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token= access_token, token_type= "bearer")


@user_router.get(path="/me", response_model=UserSchema)
async def get_user_from_token_router(current_user: User = Depends(get_current_user_from_token)):
    return current_user


@user_router.get("/private")
async def private(auth_result: str = Security(auth.verify)):
    return auth_result


@user_router.get(path="/my-incoming-messages", response_model=List[NotificationSchema])
async def get_all_user_messages_router(session: AsyncSession = Depends(get_session),
                                       current_user: User = Depends(get_current_user_from_token)):
    all_messages = await UserRepository(session=session).get_messages_for_user(user_id=current_user.id)
    return all_messages


@user_router.patch(path="/my-incoming-messages/{message_id}", response_model=NotificationReadSchema)
async def mark_as_read_message_router(message_id: int,
                                      session: AsyncSession = Depends(get_session),
                                      current_user: User = Depends(get_current_user_from_token)):
    read_message = await NotificationRepository(session=session).mark_message_as_read(message_id=message_id, user_id=current_user.id)
    return read_message
