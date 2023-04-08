from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.models.image_raiting import ImageRating
from app.schemas.image_raitings import ImageRatingUpdate


class ImageRatingService:
    @staticmethod
    async def delete_rating(rating_id: int, db: AsyncSession):
        """
        The delete_rating function deletes a rating from the database.

        :param rating_id: int: Specify the id of the rating that is to be deleted
        :param db: AsyncSession: Pass the database session to the function
        :return: A rating object
        """
        rating = await db.get(ImageRating, rating_id)
        if not rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
        await db.delete(rating)
        await db.commit()
        return rating

    @staticmethod
    async def get_all_ratings(image_id: int, db: AsyncSession):
        """
        The get_all_ratings function returns all ratings for a given image.

        :param image_id: int: Specify the image_id of the image we want to get all ratings for
        :param db: AsyncSession: Pass in the database session
        :return: A list of dictionaries
        """

        ratings = await db.scalars(select(ImageRating).filter(ImageRating.image_id == image_id))

        return ratings.all()  # noqa

    @staticmethod
    async def get_rating_by_id(rating_id: int, db: AsyncSession) -> ImageRating:
        """
        The get_rating_by_id function takes in a rating_id and an AsyncSession object.
        It then queries the database for the ImageRating with that id, and returns it.

        :param rating_id: int: Specify the id of the rating that is being queried
        :param db: AsyncSession: Pass the database connection to the function
        :return: A rating object from the database
        """
        rating = await db.scalar(select(ImageRating).filter(ImageRating.id == rating_id))
        return rating

    @staticmethod
    async def delete_rating_by_id(rating_id: int, db: AsyncSession) -> bool:
        """
        The delete_rating_by_id function deletes a rating from the database.
            Args:
                rating_id (int): The id of the image to be deleted.
                db (AsyncSession): An async session object for interacting with the database.

        :param rating_id: int: Specify the id of the rating that is to be deleted
        :param db: AsyncSession: Pass in the database session to be used for the function
        :return: A boolean value
        """
        rating = await ImageRatingService.get_rating_by_id(rating_id, db)
        if rating:
            await db.delete(rating)
            await db.commit()
            return True
        return False

    @staticmethod
    async def create(rating: int, image_id: int, user_id: int, db: AsyncSession) -> ImageRating | None:
        """
        The create function creates a new ImageRating object and adds it to the database.

        :param rating: int: Create a new rating object
        :param image_id: int: Specify the image_id of the rating
        :param user_id: int: Specify the user_id of the rating
        :param db: AsyncSession: Pass the database session to the function
        :return: The new rating object
        """
        try:
            rating = ImageRating(rating=rating, image_id=image_id, user_id=user_id)
            db.add(rating)
            await db.commit()
            await db.refresh(rating)
            return rating
        except Exception as e:
            return None



    @staticmethod
    async def update(rating_id: int, user: User, body: ImageRatingUpdate, db: AsyncSession) -> ImageRating:

        """
        The update function updates the rating of an image.
        ---
        put:
          tags: [ImageRating]

        :param rating_id: int: Identify the rating to be updated
        :param user: User: Pass the user object to the function
        :param body: ImageRatingUpdate: Pass in the rating value from the request body
        :param db: AsyncSession: Pass the database session to the function
        :return: The updated rating object
        :doc-author: Trelent
        """
        rating = await db.scalar(
                select(ImageRating).filter(and_(ImageRating.id == rating_id, ImageRating.user_id == user.id)))
        if rating:
            rating.rating = body.rating
            await db.commit()

            await db.refresh(rating)

        return rating