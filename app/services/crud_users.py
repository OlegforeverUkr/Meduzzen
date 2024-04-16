from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.schemas.users import UserCreateSchema, UserUpdateRequestSchema
from passlib.hash import pbkdf2_sha256
import logging

logger = logging.getLogger("uvicorn")



async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreateSchema):
    hashed_password = pbkdf2_sha256.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"User created with ID: {db_user.id}")
    return db_user


async def update_user(db: AsyncSession, user_id: int, user: UserUpdateRequestSchema):
    db_user = await get_user(db, user_id)
    if db_user:
        if user.username:
            db_user.username = user.username
            logger.info(f"User with ID: {db_user.id} changed {db_user.username} to {user.username}")
        if user.email:
            db_user.email = user.email
            logger.info(f"User with ID: {db_user.id} changed {db_user.email} to {user.email}")
        if user.password:
            db_user.hashed_password = pbkdf2_sha256.hash(user.password)
            logger.info(f"User with ID: {db_user.id} changed password.")
        await db.commit()
        await db.refresh(db_user)
    logger.info(f"User with ID: {db_user.id} is updated")
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
        logger.info(f"User is deleted")
