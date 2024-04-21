from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.db.connect_db import get_session
from app.utils.helpers import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.AUTH0_ALGORITHMS])
        user_email: str = payload.get("sub")
        if not user_email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(session=session, user_email=user_email)
    if user is None:
        raise credentials_exception
    return user