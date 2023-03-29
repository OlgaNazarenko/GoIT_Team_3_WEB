from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.shemas.users import UserModel
from src.services.gravatar import get_gravatar


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: Session: Access the database
    :return: A user object
    """
    user = User(
        avatar=get_gravatar(body.email),
        **body.dict(),
    )

    user.role = 'admin'

    async with db.begin():
        db.add(user)

        await db.commit()

    await db.refresh(user)

    return user


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists, it returns None.

    :param email: str: Specify the type of the parameter
    :param db: Session: Pass the database session to the function
    :return: A single user or none if the user does not exist
    """
    return await db.scalar(
        select(User)
        .filter(User.email == email)
    )


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    """
    The get_user_by_id function returns a user object from the database, given an id.

    :param user_id: int: Specify the type of the parameter
    :param db: Session: Pass in the database session
    :return: A single user object
    """
    return await db.scalar(
        select(User)
        .filter(User.id == user_id)
    )


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Get the user object from the database
    :param token: str | None: Specify that the token parameter can be a string or none
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar(user_id: int, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user in the database.

    :param user_id: int: Filter the user to update
    :param url: str: Set the avatar url of a user
    :param db: Session: Pass the database session to the function
    :return: The updated user
    """
    async with db.begin():
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
    The update_password function updates the password of a user in the database.

    :param user_id: int: Identify the user to update
    :param password: str: Update the password of a user
    :param db: Session: Pass the database session to the function
    :return: The updated user
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


async def update_email(user_id: int, email: str, db: AsyncSession) -> User:
    """
    The update_email function updates the email of a user in the database.

    :param user_id: int: Specify the user id of the user whose email we want to update
    :param email: str: Pass the new email address to update the database with
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    async with db.begin():
        user = await db.scalar(
            update(User)
            .values(email=email)
            .filter(User.id == user_id)
            .returning(User)
        )
        await db.commit()

    await db.refresh(user)

    return user


async def confirmed_email(user: User, db: AsyncSession) -> None:
    """
    The confirmed_email function is called when a user confirms their email address.
    It sets the confirmed field of the User object to True, and commits it to the database.

    :param user: User: Pass the user object to the function
    :param db: Session: Access the database
    :return: None
    """
    user.confirmed = True
    await db.commit()
