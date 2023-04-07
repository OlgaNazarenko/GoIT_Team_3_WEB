from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connect import get_db
from app.database.models import User, Image
from app.database.models.image_raiting import ImageRating
from app.schemas.image_raitings import ImageRatingCreate, ImageRatingUpdate
from app.services.auth import AuthService
from app.services.image_ratings import ImageRatingService


router = APIRouter(prefix="/images/ratings", tags=["Image ratings"])


@router.post("/{image_id}", response_model=ImageRating)
async def create_image_rating(
    image_id: int,
    rating_data: ImageRatingCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db_session = Depends(get_db)
):
    """
    The create_image_rating function creates a new image rating.

    :param image_id: int: Get the image by id
    :param rating_data: ImageRatingCreate: Validate the data that is passed to the function
    :param current_user: User: Get the current user from the authservice
    :param db_session: Get the database session
    :return: A new imagerating object, which is then serialized by the framework and returned to the client
    """
    image = await Image.get_image_by_id(db_session, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rate own image")
    rating = await ImageRatingService.create(db_session, **rating_data.dict(), image_id=image_id, user_id=current_user.id)
    return rating


@router.put("/{image_id}/{rating_id}", response_model=ImageRating)
async def update_image_rating(
    rating_id: int,
    rating_data: ImageRatingUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db_session=Depends(get_db),
):
    """
    The update_image_rating function updates an image rating.

    :param rating_id: int: Specify the id of the rating to be deleted
    :param rating_data: ImageRatingUpdate: Validate the request body
    :param current_user: User: Get the current user from the database
    :param db_session: Pass the database session to the function
    :param : Get the current user
    :return: A rating object
    """
    rating = await ImageRatingService.get_rating_by_id(rating_id, db_session)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    rating = await rating.update(db_session, **rating_data.dict())
    return rating


@router.delete("/ratings/{rating_id}")
async def delete_image_rating(
        rating_id: int,
        current_user: User = Depends(AuthService.get_current_user),
        db_session=Depends(get_db)
):
    """
    The delete_image_rating function deletes an image rating.

    :param rating_id: int: Specify the id of the rating to be deleted
    :param current_user: User: Get the current user
    :param db_session: Get the database session
    :return: A dictionary with a message
    """
    rating = await ImageRatingService.get_rating_by_id(db_session, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    if AuthService.is_admin_or_moderator(current_user):
        await ImageRatingService.delete_rating_by_id(db_session, rating_id)
    elif rating.user_id == current_user.id:
        await ImageRatingService.delete_rating_by_id(db_session, rating_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return {"message": "Rating deleted"}


@router.get("/{image_id}/ratings", response_model=List[ImageRating])
async def get_all_image_ratings(image_id: int, db_session = Depends(get_db)):
    """
    The get_all_image_ratings function returns all ratings for a given image.
        ---
        get:
            description: Get all ratings for an image.
            responses:  # This is the response that will be returned if the request is successful.  The HTTP status code 200 means &quot;OK&quot;.   The schema defines what data will be returned in the response body, and how it should look (i.e., what fields are included).   In this case, we're returning a list of ImageRating objects (see models/image_rating_model) with each object having an id field and a rating field (both integers).  We also

    :param image_id: int: Specify the image id
    :param db_session: Pass the database session to the function
    :return: A list of imagerating objects
    """
    ratings = await ImageRatingService.get_all_ratings(db_session, image_id)
    return ratings
