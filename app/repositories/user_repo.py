from sqlalchemy.exc import DatabaseError
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models import User
from app.schemas.users import UserCreateSchema, UserUpdateRequestSchema

from app.services.handlers_errors import get_or_404
from app.services.password_hash import PasswordHasher
from app.utils.helpers import check_user_by_username_exist, check_user_by_email_exist
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
        hashed_password = PasswordHasher.get_password_hash(user.password)
        try:
            await check_user_by_username_exist(self.session, user.username)
            await check_user_by_email_exist(self.session, user.email)

            db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            logger.info(f"User created with ID: {db_user.id}")
            return db_user
        except DatabaseError as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def update_user(self, user_id: int, user: UserUpdateRequestSchema):
        db_user = await get_or_404(session=self.session, id=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user:
            if user.username:
                await check_user_by_username_exist(self.session, user.username, user_id)
            if user.email:
                await check_user_by_email_exist(self.session, user.email, user_id)

            updated_values = user.dict(exclude_unset=True)
            for field, value in updated_values.items():
                if field not in db_user.__dict__:
                    raise ValueError(f"Field '{field}' does not exist in user object.")

                if field == "password":
                    value = PasswordHasher.get_password_hash(value)
                setattr(db_user, field, value)

            await self.session.commit()
            await self.session.refresh(db_user)
            logger.info(f"User with ID: {db_user.id} is updated")
            return db_user
        else:
            raise HTTPException(status_code=404, detail="User not found")


    async def delete_user(self, user_id: int):
        db_user = await get_or_404(session=self.session, id=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user:
            await self.session.delete(db_user)
            await self.session.commit()
            logger.info(f"User is deleted")
        else:
            raise HTTPException(status_code=404, detail="User not found")



    async def get_users(self, skip: int = 0, limit: int = 10):
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()



    async def get_user_by_username(self, username: str):
        getting_user = await self.session.execute(
            select(User).filter(User.username == username)
        )
        user = getting_user.scalar()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user



    async def get_user_by_email(self, user_email: str):
        getting_user = await self.session.execute(
            select(User).filter(User.email == user_email)
        )
        user = getting_user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
