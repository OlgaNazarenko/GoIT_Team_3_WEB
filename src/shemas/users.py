from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=3, max_length=100)
    last_name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    avatar: str
    confirmed: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    old_password: str = Field(min_length=6, max_length=10)
    new_password: str = Field(min_length=6, max_length=10)


class EmailModel(BaseModel):
    email: EmailStr
