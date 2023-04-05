from typing import Optional

from pydantic import EmailStr, constr

from .core import DateTimeModelMixin, IDModelMixin, CoreModel


class UserBase(CoreModel):
    """
    Leaving off password and salt from base model
    """
    username: str
    email: str
    first_name: str
    last_name: str
    avatar: str
    role: str
    email_verified: bool


class UserPublic(DateTimeModelMixin, UserBase, IDModelMixin):
    class Config:
        orm_mode = True


class UserCreate(CoreModel):
    username: constr(min_length=3, max_length=20, regex="[a-zA-Z0-9_-]+$")
    email: EmailStr
    first_name: constr(min_length=3, max_length=100)
    last_name: constr(min_length=3, max_length=100)
    password: constr(min_length=6, max_length=20)


class UserCreateResponse(CoreModel):
    user: UserPublic
    detail: str = "User successfully created"


class UserProfile(UserPublic):
    num_photos: int

    class Config:
        orm_mode = True


class ProfileUpdate(CoreModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TokenResponse(CoreModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserPasswordUpdate(CoreModel):
    old_password: constr(min_length=6, max_length=20)
    new_password: constr(min_length=6, max_length=20)


class EmailModel(CoreModel):
    email: EmailStr
