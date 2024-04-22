from typing import Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.config import settings
from app.utils.exeptions_auth import UnauthenticatedException, UnauthorizedException



class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self):
        jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self, token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())):
        if not token:
            raise UnauthenticatedException

        try:
            payload = jwt.decode(
                token.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.AUTH0_ALGORITHMS],
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=settings.AUTH0_ISSUER,
            )
        except JWTError as error:
            raise UnauthorizedException(str(error))

        return payload
