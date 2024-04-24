from datetime import datetime
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import ExpiredSignatureError, JWTError
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.db.connect_db import get_session
from app.repositories.user_repo import UserRepository
from app.utils.exeptions_auth import UnauthorizedException
from app.utils.helpers import check_user_by_email_exist
from app.services.crate_user_from_token import create_user_from_auth_token

oauth2_scheme = HTTPBearer()


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SIGNING_KEY,
            algorithms=[settings.AUTH0_ALGORITHMS],
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=settings.AUTH0_ISSUER,
        )
        email: str = payload.get("email")

        exists_user = await check_user_by_email_exist(session=session, email=email)

        if not exists_user:
            creation_user = await create_user_from_auth_token(session=session, email=email)
            return creation_user
        else:
            expiration_time = datetime.fromtimestamp(payload.get("exp"))
            current_time = datetime.now()

            if expiration_time < current_time:
                raise ExpiredSignatureError("Token has expired")

            return exists_user

    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")

