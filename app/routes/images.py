import asyncio

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User
from app.repository import images as repository_images
from app.models.image import (
    ImageResponse,
    ImageModel,
)
from app.services import cloudinary
from app.services.auth import auth_service


router = APIRouter(prefix="/images", tags=["images"])



@router.post("/image", response_model=ImageResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upload_image(description, file: UploadFile = File(), db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The upload_image function uploads the image to Cloudinary.

    :param file: UploadFile: Get the file that is uploaded
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: The uploaded image
    """
    loop = asyncio.get_event_loop()
    file_id = await loop.run_in_executor(None, cloudinary.upload_image, file.file)


    return await repository_images.create_image(current_user.id, description, file_id, db)
