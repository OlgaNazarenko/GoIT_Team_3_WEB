import asyncio

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User
from app.repository import users as repository_users
from app.schemas.user import (
    UserPublic,
    UserPasswordUpdate,
    EmailModel,
    ProfileUpdate,
    UserProfile
)
from app.services import cloudinary
from app.services.auth import auth_service


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_me function returns the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_avatar(file: UploadFile = File(), db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_avatar function updates the avatar of a user.

    :param file: UploadFile: Get the file that is uploaded
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: The updated user object
    """
    loop = asyncio.get_event_loop()
    file_id = await loop.run_in_executor(None, cloudinary.upload_image, file.file)

    if file_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    avatar_url = await loop.run_in_executor(None, cloudinary.get_format_image, file_id)

    return await repository_users.update_avatar(current_user.id, avatar_url, db)


@router.patch("/email", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_email(body: EmailModel, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_email function updates the email of a user.
        The function takes in an EmailModel object, which contains the new email address to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param body: EmailModel: Get the email from the request body
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A user object
    """
    updated_user = await repository_users.update_email(current_user.id, body.email, db)

    if updated_user is None:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="An account with this email address already exists")

    return updated_user


@router.patch("/password", response_model=UserPublic, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_password(body: UserPasswordUpdate, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_password function takes in a ChangePassword object, which contains the old and new passwords.
    It then verifies that the old password is correct, hashes the new password, and updates it in the database.

    :param body: ChangePassword: Pass the old and new password to the function
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A dictionary with the following keys:
    """
    if not auth_service.verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")

    password = auth_service.get_password_hash(body.new_password)

    return await repository_users.update_password(current_user.id, password, db)


@router.get("/{user_id}/profile", response_model = UserProfile,
            dependencies = [Depends(RateLimiter(times = 10, seconds = 60))])
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)) -> UserProfile:
    """
    The get_user_profile function is used to retrieve a user's profile information.
        It takes in the user_id of the desired profile and returns a UserPublic object containing all publically available
        information about that user.

    :param user_id: int: Get the user_id from the path
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the user object of the currently logged in user
    :return: A model of UserProfile object
    """
    user = await repository_users.get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "No profile found with that username.")

    num_photos = await repository_users.get_num_photos_by_user(user_id, db)

    user_profile = UserProfile(
        id = user.id,
        username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        avatar = user.avatar,
        role = user.role,
        created_at = user.created_at,
        updated_at =user.updated_at,
        email_verified =user.email_verified,
        num_photos = num_photos
    )

    return user_profile


@router.put("/{user_id}/update", response_model=UserPublic)
async def update_user_profile(body: ProfileUpdate, user_id: int, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user)) -> UserPublic:
    """
    The update_user_profile function updates a user's profile.

    :param body: ProfileUpdate: Specify the type of data that is expected to be passed in
    :param user_id: int: Get the user by id
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Get the current user's id
    :return: A model of UserPublic object
    """
    user = await repository_users.get_user_by_id(current_user.id, db)

    # if the current user is not the user being updated
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to update this user.")

    return await repository_users.update_user_profile(body, user_id, db)


@router.patch("/{user_id}/partial_update", response_model=UserPublic)
async def partial_update_user_profile(user_id: int,
                                      username: str = None,
                                      first_name: str = None,
                                      last_name: str = None,
                                      db: AsyncSession = Depends(get_db),
                                      current_user: User = Depends(auth_service.get_current_user)) -> UserPublic:
    """
    The partial_update_user_profile function allows a user to update their username, first name, and/or last name.

    :param user_id: int: Identify the user to be updated
    :param username: str: Get the username from the request body
    :param first_name: str: Update the first name of a user
    :param last_name: str: Update the last name of a user
    :param db: AsyncSession: Get the database connection
    :param current_user: User: Get the current user from the database
    :return: The updated user's public information
    """
    user = await repository_users.get_user_by_id(current_user.id, db)

    # if the current user is not the user being updated
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to update this user.")

    # make sure username isn't already taken
    if username and await repository_users.get_user_by_username(db = db, username = username):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "That username is already taken. Please try another one."
        )

    return await repository_users.partial_update_user_profile(db, user_id, username, first_name, last_name)
