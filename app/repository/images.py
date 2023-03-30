from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Image


async def create_image(user_id: int, description: str, uuid: str, db: AsyncSession) -> Image:
    """
    The create_image function creates a new image in the database.

    :param current_user: int: Get the current user
    :param description: str: Get description for image
    :param uuid: str: Get hash for image
    :param db: AsyncSession: Pass in the database session to the function
    :return: A user object
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