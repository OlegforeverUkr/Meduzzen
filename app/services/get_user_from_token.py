from datetime import datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.db.connect_db import get_session
from app.repositories.user_repo import UserRepository
from app.utils.exeptions_auth import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(token, key=settings.SIGNING_KEY, algorithms=[settings.AUTH0_ALGORITHMS])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user id from token")
        expiration_time = datetime.fromtimestamp(payload.get("exp"))
        current_time = datetime.now()

        if expiration_time < current_time:
            raise ExpiredSignatureError("Token has expired")
    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")

    user = await UserRepository(session=session).get_user(user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user