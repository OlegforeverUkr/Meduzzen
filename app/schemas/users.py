from pydantic import BaseModel, EmailStr, constr, field_validator
from app.utils.helpers import password_valid_regex

MIN_LEN_USERNAME = 2


class UserCreateSchema(BaseModel):
    username: constr(min_length=2, max_length=100)
    email: EmailStr
    password: constr(min_length=6)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "example_user",
                "email": "user@example.com",
                "password": "secure_password"
            },
            "strip_whitespace": True
        }

    @field_validator('password', mode='before')
    def validate_password(cls, value):
        if not password_valid_regex.match(value):
            raise ValueError('Password must contain at least 6 characters, one letter, one number, and one special character')
        return value

    @field_validator('username', mode='before')
    def validate_username(cls, value):
        username = value.replace(" ", "")
        if len(username) < MIN_LEN_USERNAME:
            raise ValueError('Username must contain at least 2 characters')
        return username


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
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


    @field_validator("email", mode='before')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError("Value cannot be None")
        return value


    @field_validator('password', mode='before')
    def validate_password(cls, value):
        if not password_valid_regex.match(value):
            raise ValueError('Password must contain at least 6 characters, one letter, one number, and one special character')
        return value


    @field_validator('username', mode='before')
    def validate_username(cls, value):
        username = value.replace(" ", "")
        if len(username) < MIN_LEN_USERNAME:
            raise ValueError('Username must contain at least 2 characters')
        return username


    class Config:
        from_attributes = True
        json_schema_extra = {
            "min_length": 2,
            "max_length": 100,
            "validate_all": True,
            "strip_whitespace": True
        }


class UsersListResponseSchema(BaseModel):
    users: list[UserSchema]
    total: int


class UserDetailResponseSchema(UserSchema):
    pass



class Token(BaseModel):
    access_token: str
    token_type: str