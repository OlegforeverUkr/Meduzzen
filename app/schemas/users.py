from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


class SignInRequest(BaseModel):
    username: str
    password: str


class SignUpRequest(UserCreate):
    pass


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UsersListResponse(BaseModel):
    users: list[User]
    total: int


class UserDetailResponse(User):
    pass
