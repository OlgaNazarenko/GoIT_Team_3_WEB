from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User
from app.repository import images as repository_images
from app.repository import image_formats as repository_image_formats
from app.schemas.image_formats import (
    ImageTransformation,
    FormattedImageCreateResponse,
    ImageFormatsResponse,
)
from app.services import cloudinary
from app.services.auth import auth_service


router = APIRouter(prefix="/formats", tags=["image formats"])


@router.post(
    '/', response_model=FormattedImageCreateResponse,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def formatting_image(body: ImageTransformation,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
    The formatting_image function is used to format an image.
        The function takes in the following parameters:
            - body: ImageTransformation, which contains the id of the image and a transformation string.
            - current_user: User, which is obtained from auth_service.get_current_user(). This parameter allows us to get
                information about who made this request (the user). We use this information to ensure that only users with
                access can make requests on their own images. If no user is found, then we raise a HTTPException with status code 401 (Unauthorized) and detail &quot;

    :param body: ImageTransformation: Get the image_id and transformation parameters
    :param current_user: User: Get the user's id
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A formatted image
    """
    image = await repository_images.get_image_by_id(current_user.id, body.image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    format_image = cloudinary.formatting_image(image.public_id, body.transformation)

    formatted_image = await repository_image_formats.create_image_format(
        current_user.id, body.image_id, format_image['format'], db
    )
    if formatted_image is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This image already has this formatting")

    formatted_image.url = format_image['url']

    return {
        "parent_image_id": body.image_id,
        "formatted_image": formatted_image,
        "detail": "Image successfully formatted"
    }


@router.get('/{image_id}', response_model=ImageFormatsResponse, response_model_by_alias=False)
async def get_image_formats(image_id: int, current_user: User = Depends(auth_service.get_current_user),
                            db: AsyncSession = Depends(get_db)):
    """
    The get_image_formats function returns a list of formatted images for the given image_id.

    :param image_id: int: Get the image by id
    :param current_user: User: Get the user id from the token
    :param db: AsyncSession: Get the database session
    :return: The original image and the formatted images
    """
    image = await repository_images.get_image_by_id(current_user.id, image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    image_formats = await repository_image_formats.get_image_formats_by_image_id(current_user.id, image_id, db)

    for image_format in image_formats:
        image_format.public_id = image.public_id

    return {"parent_image": image, "formatted_images": image_formats}
