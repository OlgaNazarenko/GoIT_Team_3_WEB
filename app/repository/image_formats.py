from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import ImageFormat, Image


async def create_image_format(user_id: int, image_id: int, format_: dict, db: AsyncSession) -> Optional[ImageFormat]:
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
    images = await db.scalars(
        select(ImageFormat)
        .filter(ImageFormat.image_id == image_id, ImageFormat.user_id == user_id)
    )

    return images.all()  # noqa
