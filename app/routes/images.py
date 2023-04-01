import asyncio

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User
from app.repository import images as repository_images
from app.schemas.image import (
    ImageCreateResponse,
    ImageGetResponse
)
from app.services import cloudinary
from app.services.auth import auth_service


router = APIRouter(prefix="/images", tags=["images"])



@router.post("/", response_model=ImageCreateResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upload_image(file: UploadFile = File(), description: str = Form(min_length=10, max_length=1200), db: AsyncSession = Depends(get_db),
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


@router.get("/", response_model=ImageGetResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def dowload_image(file_id: str, current_user: User = Depends(auth_service.get_current_user)):
    """
    The dowload_image function dowloads the image from Cloudinary.

    :param file_id: str: Get the file_url to dowload
    :return: The dowload image
    """
    if current_user:
        
        loop = asyncio.get_event_loop()
        try:
            url = await loop.run_in_executor(None, cloudinary.get_format_image, file_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Url does not exist")

        return url
