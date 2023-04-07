import asyncio
from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User, UserRole
from app.repository import images as repository_images
from app.schemas.image import (
    ImageCreateResponse,
    ImagePublic,
)
from app.services import cloudinary
from app.services.auth import get_current_active_user


router = APIRouter(prefix="/images", tags=["Images"])


#  TODO tags validation
#  TODO maximum 5 tags
@router.post(
    "/", response_model=ImageCreateResponse, response_model_by_alias=False, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def upload_image(
        file: UploadFile = File(), description: str = Form(min_length=10, max_length=1200),
        tags: list[str] = Form(alias="tag", min_length=3, max_length=50),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    The upload_image function is used to upload an image file to the cloudinary server.
    The function takes in a file, description, and tags as parameters. The file parameter is required and must be of type UploadFile (a FastAPI File).
    The description parameter is optional but if provided it must be between 10-1200 characters long. The tags parameter is also optional but if provided
    it must contain at least 3 words with each word being no longer than 50 characters long.

    :param file: UploadFile: Get the file from the request
    :param description: str: Get the description of the image
    :param tags: list[str]: Receive a list of tags from the client
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :param : Specify the type of file that will be uploaded
    :return: A dictionary with the image and a detail message
    """
    loop = asyncio.get_event_loop()
    image = await loop.run_in_executor(None, cloudinary.upload_image, file.file)

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    image = await repository_images.create_image(current_user.id, description.strip(), tags, image['public_id'], db)

    return {"image": image, "detail": "Image successfully uploaded"}


@router.get("/{image_id}", response_model=ImagePublic, dependencies=[Depends(RateLimiter(times=10, seconds=10))])
async def get_image(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_image function returns an image by its id.

    :param image_id: int: Get the image id from the url
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The image object
    """
    image = await repository_images.get_image_by_id(image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    return image


# TODO нужно еще добавить возможность изменения тегов картинки
@router.patch("/description", response_model=ImagePublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_description(
        image_id: int,
        description: str = Form(min_length=10, max_length=1200),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_description function updates the description of an image.
        The function takes in the description to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param image_id: int: Get the unique link from the request
    :param description: Form: Get the description from the request
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: An image object
    """
    image = await repository_images.get_image_by_id(image_id, db)

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Not found image")

    if current_user.role != UserRole.admin or image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updated_image = await repository_images.update_description(image_id, description, db)

    return updated_image


@router.delete("/", response_model=ImagePublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_image(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The delete_image function deletes an image from the database.
        Args:
            image_id (int): The id of the image to be deleted.
            db (AsyncSession, optional): An async session with a database connection. Defaults to Depends(get_db).

    :param image_id: int: Get the image by id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: The deleted image
    """
    image = await repository_images.get_image_by_id(image_id, db)

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Not found image")

    if current_user.role != UserRole.admin or image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    deleted_image = await repository_images.delete_image(image_id, db)

    return deleted_image
