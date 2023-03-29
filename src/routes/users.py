import asyncio

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.shemas.users import (
    UserDb,
    ChangePassword,
    EmailModel,
)
from src.services import cloudinary
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_me function returns the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=UserDb, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_avatar(file: UploadFile = File(), db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_avatar function updates the avatar of a user.

    :param file: UploadFile: Get the file that is uploaded
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: The updated user object
    """
    loop = asyncio.get_event_loop()
    avatar = await loop.run_in_executor(None, cloudinary.upload_image, file.file, current_user.id)

    return await repository_users.update_avatar(current_user.id, avatar, db)


@router.patch("/email", response_model=UserDb, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_email(body: EmailModel, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_email function updates the email of a user.
        The function takes in an EmailModel object, which contains the new email address to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param body: EmailModel: Get the email from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A user object
    """
    return await repository_users.update_email(current_user.id, body.email, db)


@router.patch("/password", response_model=UserDb, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_password(body: ChangePassword, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_password function takes in a ChangePassword object, which contains the old and new passwords.
    It then verifies that the old password is correct, hashes the new password, and updates it in the database.

    :param body: ChangePassword: Pass the old and new password to the function
    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A dictionary with the following keys:
    """
    if not auth_service.verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")

    password = auth_service.get_password_hash(body.new_password)

    return await repository_users.update_password(current_user.id, password, db)
