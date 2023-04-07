from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Image, Tag
from sqlalchemy import update
from typing import Optional
from sqlalchemy.orm.exc import UnmappedInstanceError

from app.repository.tags import get_or_create_tags


async def get_image_by_id(image_id: int, db: AsyncSession) -> Image:
    """
    The get_image_by_id function returns an image from the database.

    :param image_id: int: Filter the images by id
    :param db: AsyncSession: Pass in the database session to use
    :return: A single image object
    """
    return await db.scalar(
        select(Image)
        .filter(Image.id == image_id)
    )


async def create_image(user_id: int, description: str, tags: list[str], public_id: str, db: AsyncSession) -> Image:
    """
    The create_image function creates a new image in the database.

    :param user_id: int: Specify the user who uploaded the image
    :param description: str: Describe the image
    :param tags: list[str]: Specify that the tags parameter is a list of strings
    :param public_id: str: Store the public id of the image in cloudinary
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    tags = await get_or_create_tags(tags, db)
    image = Image(
        user_id=user_id,
        description=description,
        tags=tags,
        public_id=public_id
    )
    db.add(image)

    await db.commit()

    await db.refresh(image)
    return image


async def update_description(image_id: int, description: str, db: AsyncSession) -> Optional[Image]:
    """
    The update_description function updates the description of an image in the database.

    :param image_id: int: Identify the image that is being updated
    :param description: str: Update the description of the image
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    try:
        async with db.begin():
            image = await db.scalar(
                update(Image)
                .values(description=description)
                .filter(Image.image_id == image_id)
                .returning(Image)
            )
            await db.commit()
        await db.refresh(image)

    except UnmappedInstanceError:
        return

    return image


async def delete_image(image_id: int, db: AsyncSession) -> Optional[Image]:
    """
    The delete_image function deletes an image in the database.
    :param image_id: str: Get identifier for the image
    :param db: AsyncSession: Pass in the database session to the function
    :return: An image object
    """
    try:
        async with db.begin():
            image = await db.scalar(
                delete(Image)
                .filter(Image.id == image_id)
                .returning(Image)
            )
    except UnmappedInstanceError:
        return

    return image


async def get_images(skip: int, limit: int, description: str, tags: list[str], user_id: int, db: AsyncSession) -> list[Image]:

    """
    The get_images function takes in a skip, limit, description, tags and user_id.
    It then queries the database for images that match the given parameters.
    If no parameters are given it will return all images.

    :param skip: int: Skip a certain number of images
    :param limit: int: Limit the number of images that are returned
    :param description: str: Filter images by description
    :param tags: list[str]: Filter the images by tags
    :param user_id: int: Filter the images by user id
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of images
    :doc-author: Trelent
    """

    query = select(Image)
    if description:
        query = query.filter(Image.description.like(f'{description}%'))
    if tags:
        query = query.filter(Image.tags.any(Tag.name.in_(tags)))
    if user_id:
        query = query.filter(Image.user_id == user_id)

    image = await db.scalars(query.offset(skip).limit(limit))

    return image.unique().all()
