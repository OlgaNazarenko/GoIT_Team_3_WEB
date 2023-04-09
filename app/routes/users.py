import asyncio
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User, UserRole
from app.repository import users as repository_users
from app.repository.users import user_update_is_active
from app.schemas.user import (
    UserPublic,
    UserPasswordUpdate,
    EmailModel,
    ProfileUpdate,
    UserProfile
)
from app.services import cloudinary
from app.services.auth import AuthService
from app.utils.filter import UserRoleFilter

from app.schemas import user as user_schemas
from app.services import cloudinary
from app.services.auth import AuthService, get_current_active_user
from app.utils.filter import UserRoleFilter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/", response_model=user_schemas.UserPublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_me(
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_me function returns the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_avatar(
        file: UploadFile = File(),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_avatar function updates the avatar of a user.

    :param file: UploadFile: Get the file that is uploaded
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: The updated user object
    """
    loop = asyncio.get_event_loop()
    image = await loop.run_in_executor(
        None, cloudinary.upload_image, file.file, current_user.avatar.rsplit('/', maxsplit=1)[1]
    )

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    avatar = cloudinary.formatting_image_url(image['public_id'], cloudinary.FORMAT_AVATAR, image['version'])

    return await repository_users.update_avatar(current_user.id, avatar['url'], db)


@router.patch("/email", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_email(
        body: user_schemas.EmailModel,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
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


@router.patch("/password", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_password(
        body: user_schemas.UserPasswordUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_password function updates the password of a user.

    :param body: UserPasswordUpdate: Get the old and new password from the request body
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user object from the database
    :return: A json response with the updated user
    """
    if not AuthService.verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")

    password = AuthService.get_password_hash(body.new_password)

    return await repository_users.update_password(current_user.id, password, db)


@router.post(
    "/change-role",
    response_model=user_schemas.UserPublic,
    dependencies=[Depends(UserRoleFilter(UserRole.admin))]
)
async def change_user_role(
        body: user_schemas.ChangeRole,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The change_user_role function is used to change the role of a user.

    :param body: user_schemas.ChangeRole: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A dictionary with the user_id and role
    """
    user = await repository_users.get_user_by_id(body.user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == body.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already has this role installed")

    return await repository_users.user_update_role(user, body.role, db)  # noqa


@router.patch("/", response_model=user_schemas.UserPublic)
async def update_user_profile(
        body: user_schemas.ProfileUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_user_profile function updates the user's profile.

    :param body: ProfileUpdate: Pass the data from the request body to this function
    :param db: AsyncSession: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A dictionary with the updated user information
    """
    if body.username and await repository_users.get_user_by_username(username=body.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That username is already taken. Please try another one."
        )

    return await repository_users.update_user_profile(current_user.id, body, db)


# TODO update method
@router.get("/{user_id}", response_model=user_schemas.UserProfile,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_user_profile(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_user function is used to retrieve a user's profile.

    :param user_id: int: Get the user id from the url
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Get the current user
    :return: A userprofile object
    """
    user = await repository_users.get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No profile found with that username.")

    num_photos = await repository_users.get_num_photos_by_user(user_id, db)

    user_profile = user_schemas.UserProfile(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        avatar=user.avatar,
        created_at=user.created_at
    )

    return user_profile


@router.patch("/", response_model=UserPublic)
async def update_user_profile(body: ProfileUpdate, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(AuthService.get_current_user)) -> UserPublic:
    """
    The update_user_profile function updates a user's profile.

    :param body: ProfileUpdate: Specify the type of data that is expected to be passed in
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Get the current user's id
    :return: A model of UserPublic object
    """
    if body.username and await repository_users.get_user_by_username(username=body.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That username is already taken. Please try another one."
        )

    return await repository_users.update_user_profile(current_user.id, body, db)


@router.post("/ban/{user_id}", dependencies=[Depends(UserRoleFilter(UserRole.admin))])
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db),
                   current_user: UserRole = Depends(AuthService.get_current_user)):
    """
    The ban_user function is used to ban a user.
    :param user_id: int: Specify the user id of the user to be banned
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: UserRole: Get the current user's role
    :return: A dictionary with a message, which is not the right way to return data
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await user_update_is_active(user, False, db)
