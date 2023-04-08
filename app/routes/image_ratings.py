from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import User, Image

from app.schemas.image_raitings import ImageRatingCreate, ImageRatingUpdate, ImageRatingResponse
from app.services.auth import AuthService
from app.services.image_ratings import ImageRatingService

router = APIRouter(prefix="/images/ratings", tags=["Image ratings"])


@router.post("/{image_id}", response_model=ImageRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_image_rating(
        rating_data: ImageRatingCreate,
        current_user: User = Depends(AuthService.get_current_user),
        db_session=Depends(get_db)
):
    """
    The create_image_rating function creates a new image rating.

    :param rating_data: ImageRatingCreate: Get the rating and image_id from the request body
    :param current_user: User: Get the current user from the database
    :param db_session: Pass the database session to the image service
    :return: A rating object
    """
    image = await Image.get_image_by_id(db_session, rating_data.image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rate own image")

    rating = await ImageRatingService.create(rating_data.rating, rating_data.image_id, current_user.id, db_session)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this image.")

    return rating


@router.put("/{image_id}/{rating_id}", response_model=ImageRatingResponse)
async def update_image_rating(
        rating_id: int,
        rating_data: ImageRatingUpdate,
        current_user: User = Depends(AuthService.get_current_user),
        db_session: AsyncSession = Depends(get_db),
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

    new_rating = await ImageRatingService.update(rating_id, current_user, rating_data, db=db_session)
    if new_rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    return new_rating


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
    rating = await ImageRatingService.get_rating_by_id(rating_id, db_session)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    if AuthService.is_admin_or_moderator(current_user):
        await ImageRatingService.delete_rating_by_id(rating_id, db_session)
    # elif rating.user_id == current_user.id:
    #     await ImageRatingService.delete_rating_by_id(rating_id, db_session)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return {"message": "Rating deleted"}


@router.get("/{image_id}/ratings")
async def get_all_image_ratings(image_id: int, current_user: User = Depends(AuthService.get_current_user),
                                db_session: AsyncSession = Depends(get_db)):
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
    ratings = await ImageRatingService.get_all_ratings(image_id, db_session)
    print(len(ratings))
    if len(ratings) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings not found")

    return ratings
