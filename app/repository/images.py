from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Image


async def get_image_by_id(user_id: int, image_id: int, db: AsyncSession) -> Image:
    """
    The get_image_by_id function returns an image from the database.

    :param user_id: int: Filter the images by user_id
    :param image_id: int: Filter the images by id
    :param db: AsyncSession: Pass in the database session to use
    :return: A single image object
    """
    return await db.scalar(
        select(Image)
        .filter(Image.id == image_id, Image.user_id == user_id)
    )


async def create_image(user_id: int, description: str, public_id: str, db: AsyncSession) -> Image:
    """
    The create_image function creates a new image in the database.

    :param user_id: int: Identify the user who uploaded the image
    :param description: str: Set the description of the image
    :param public_id: str: Identify the image
    :param db: AsyncSession: Pass in the database session to be used
    :return: An image object
    """
    image = Image(
        user_id=user_id,
        description=description,
        public_id=public_id
    )
    db.add(image)

    await db.commit()

    await db.refresh(image)

    return image
