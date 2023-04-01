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
