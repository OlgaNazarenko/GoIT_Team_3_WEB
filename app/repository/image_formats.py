from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ImageFormat, Image


async def create_image_format(user_id: int, image_id: int, format_: dict, db: AsyncSession) -> Optional[ImageFormat]:
    """
    The create_image_format function creates a new image format in the database.

    :param user_id: int: Identify the user that is creating the image format
    :param image_id: int: Specify the image that the format is for
    :param format_: dict: Pass the format of the image
    :param db: AsyncSession: Pass the database session to the function
    :return: An imageformat object
    """
    try:
        format_ = ImageFormat(
            format=format_,
            user_id=user_id,
            image_id=image_id,
        )
        db.add(format_)

        await db.commit()

        await db.refresh(format_)

        return format_
    except IntegrityError:
        return


async def get_image_formats_by_image_id(user_id: int, image_id: int, db: AsyncSession) -> list[Image]:
    """
    The get_image_formats_by_image_id function returns a list of ImageFormat objects that are associated with the
    image_id parameter. The user_id parameter is used to ensure that only images belonging to the user are returned.

    :param user_id: int: Identify the user
    :param image_id: int: Filter the images by image_id
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of imageformat objects
    """
    images = await db.scalars(
        select(ImageFormat)
        .filter(ImageFormat.image_id == image_id, ImageFormat.user_id == user_id)
    )

    return images.all()  # noqa
