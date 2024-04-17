from sqlalchemy.exc import DatabaseError
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models import User
from app.schemas.users import UserCreateSchema, UserUpdateRequestSchema
from passlib.hash import pbkdf2_sha256
from app.services.handlers_errors import get_or_404
import logging

logger = logging.getLogger("uvicorn")


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_user(self, user_id: int):
        try:
            result = await get_or_404(session=self.session, id=user_id)
            return result
        except DatabaseError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


    async def create_user(self, user: UserCreateSchema):
        hashed_password = pbkdf2_sha256.hash(user.password)
        try:
            existing_user_with_username = await self.session.execute(
                select(User).filter(User.username == user.username)
            )
            existing_user_with_email = await self.session.execute(
                select(User).filter(User.email == user.email)
            )
            if existing_user_with_username.scalar():
                raise HTTPException(status_code=400, detail="Username already exists")
            if existing_user_with_email.scalar():
                raise HTTPException(status_code=400, detail="Email already exists")


            db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            logger.info(f"User created with ID: {db_user.id}")
            return db_user
        except DatabaseError as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def update_user(self, user_id: int, user: UserUpdateRequestSchema):
        try:
            db_user = await get_or_404(session=self.session, id=user_id)
            if db_user:

                if user.username:
                    existing_user_with_username = await self.session.execute(
                        select(User).filter(User.username == user.username)
                    )
                    if existing_user_with_username.scalar() and existing_user_with_username.scalar().id != user_id:
                        raise HTTPException(status_code=400, detail="Username already exists")
                if user.email:
                    existing_user_with_email = await self.session.execute(
                        select(User).filter(User.email == user.email)
                    )
                    if existing_user_with_email.scalar() and existing_user_with_email.scalar().id != user_id:
                        raise HTTPException(status_code=400, detail="Email already exists")

                updated_values = user.dict(exclude_unset=True)
                for field, value in updated_values.items():
                    if field == "password":
                        value = pbkdf2_sha256.hash(value)
                    setattr(db_user, field, value)
                    logger.info(f"User with ID: {db_user.id} changed {field} to {value}")
                await self.session.commit()
                await self.session.refresh(db_user)
                logger.info(f"User with ID: {db_user.id} is updated")
                return db_user
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except DatabaseError as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def delete_user(self, user_id: int):
        try:
            db_user = await get_or_404(session=self.session, id=user_id)
            if db_user:
                await self.session.delete(db_user)
                await self.session.commit()
                logger.info(f"User is deleted")
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except DatabaseError as e:
            raise HTTPException(status_code=400, detail=str(e))



    async def get_users(self, skip: int = 0, limit: int = 10):
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
