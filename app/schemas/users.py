from typing import ClassVar

from pydantic import BaseModel, EmailStr, config
from pydantic_settings import BaseSettings


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config(config.ConfigDict):
        from_attributes = True


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config(config.ConfigDict):
        from_attributes = True


class SignInRequestSchema(BaseModel):
    username: str
    password: str


class SignUpRequestSchema(UserCreateSchema):
    pass


class UserUpdateRequestSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UsersListResponseSchema(BaseModel):
    users: list[UserSchema]
    total: int


class UserDetailResponseSchema(UserSchema):
    pass
