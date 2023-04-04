from typing import Optional

from sqlalchemy import select, update, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.schemas.user import UserCreate
from app.services.gravatar import get_gravatar


async def create_user(body: UserCreate, db: AsyncSession) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: AsyncSession: Pass in the database session to the function
    :return: A user object
    """
    user = User(
        avatar=await get_gravatar(body.email),
        **body.dict(),
    )
    db.add(user)

    await db.commit()

    await db.refresh(user)

    return user


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    The get_user_by_email function returns a user object from the database
    based on the email address provided. If no user is found, None is returned.

    :param email: str: Pass the email address to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A single user or none
    """
    return await db.scalar(
        select(User)
        .filter(User.email == email)
    )


async def get_user_by_email_or_username(email: str, username: str, db: AsyncSession) -> Optional[User]:
    """
    The get_user_by_email_or_username function returns a user object if the email or username is found in the database.

    :param email: str: Pass the email address of a user to the function
    :param username: str: Filter the database by username
    :param db: AsyncSession: Pass the database session to the function
    :return: The first user that matches the email or username
    """
    return await db.scalar(
        select(User)
        .filter(or_(User.email == email, User.username == username))
    )


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    """
    The get_user_by_id function returns a user object from the database.

    :param user_id: int: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: A single user object
    """
    return await db.scalar(
        select(User)
        .filter(User.id == user_id)
    )


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify which user the token is for
    :param token: str | None: Specify the type of token
    :param db: AsyncSession: Commit the changes to the database
    :return: None
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar(user_id: int, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param user_id: int: Specify the user's id
    :param url: str: Pass the url of the avatar to be updated
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    """
    user = await db.scalar(
        update(User)
        .values(avatar=url)
        .filter(User.id == user_id)
        .returning(User)
    )

    await db.commit()

    await db.refresh(user)

    return user


async def update_password(user_id: int, password: str, db: AsyncSession) -> User:
    """
    The update_password function updates the password of a user.

    :param user_id: int: Identify the user to update
    :param password: str: Update the password of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object, which is the updated user
    """
    async with db.begin():
        user = await db.scalar(
            update(User)
            .values(password=password)
            .filter(User.id == user_id)
            .returning(User)
        )
        await db.commit()

    await db.refresh(user)

    return user


async def update_email(user_id: int, email: str, db: AsyncSession) -> Optional[User]:
    """
    The update_email function updates the email of a user.

    :param user_id: int: Identify the user to update
    :param email: str: Update the email of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated user object
    """
    try:
        async with db.begin():
            user = await db.scalar(
                update(User)
                .values(email=email)
                .filter(User.id == user_id)
                .returning(User)
            )
            await db.commit()
    except IntegrityError as e:
        return

    # await db.refresh(user)

    return user


async def confirmed_email(user: User, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.

    :param user: User: Pass the user object to the function
    :param db: AsyncSession: Pass in a database session
    :return: None
    """
    user.email_verified = True
    await db.commit()
