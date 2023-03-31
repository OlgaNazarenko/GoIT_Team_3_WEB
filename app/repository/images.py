from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Image


async def create_image(user_id: int, description: str, uuid: str, db: AsyncSession) -> Image:
    """
    The create_image function creates a new image in the database.

    :param user_id: int: Identify the user who uploaded the image
    :param description: str: Set the description of the image
    :param uuid: str: Identify the image
    :param db: AsyncSession: Pass in the database session to be used
    :return: An image object
    """
    image = Image(
        user_id=user_id,
        description=description,
        uuid=uuid
    )
    db.add(image)

    await db.commit()

    await db.refresh(image)

    return image
