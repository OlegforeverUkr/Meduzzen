from datetime import datetime
from datetime import timedelta

from app.core.config import settings
from jose import jwt


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    to_encode["iss"] = settings.AUTH0_ISSUER
    encoded_jwt = jwt.encode(to_encode,
                             key=settings.SECRET_KEY,
                             algorithm=settings.AUTH0_ALGORITHMS)
    return encoded_jwt