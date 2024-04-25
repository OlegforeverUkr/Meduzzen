from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserCreateSchema
from app.repositories.user_repo import UserRepository


async def create_user_from_auth_token(session: AsyncSession, email: str):
    username = "auth0" + email.split("@")[0]
    password_prefix = "Auth0!" + datetime.now().strftime("%Y%m%d%H%M")
    password = password_prefix + email.split("@")[0]
    new_user_schema = UserCreateSchema(username=username, email=email, password=password)

    user_new = await UserRepository(session=session).create_user(new_user_schema)

    return user_new