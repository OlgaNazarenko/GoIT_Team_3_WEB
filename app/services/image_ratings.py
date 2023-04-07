from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.image_raiting import ImageRating


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
        ratings = await db.execute(
            ImageRating.__table__.select().where(ImageRating.image_id == image_id)
        )
        return ratings.fetchall()

    @staticmethod
    async def get_rating_by_id(rating_id: int, db: AsyncSession) -> ImageRating:
        """
        The get_rating_by_id function takes in a rating_id and an AsyncSession object.
        It then queries the database for the ImageRating with that id, and returns it.

        :param rating_id: int: Specify the id of the rating that is being queried
        :param db: AsyncSession: Pass the database connection to the function
        :return: A rating object from the database
        """
        rating = await db.query(ImageRating).filter(ImageRating.id == rating_id).first()
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
    async def create(rating: int, image_id: int, user_id: int, db: AsyncSession) -> ImageRating:
        """
        The create function creates a new ImageRating object and adds it to the database.

        :param rating: int: Create a new rating object
        :param image_id: int: Specify the image_id of the rating
        :param user_id: int: Specify the user_id of the rating
        :param db: AsyncSession: Pass the database session to the function
        :return: The new rating object
        """
        rating = ImageRating(rating=rating, image_id=image_id, user_id=user_id)
        db.add(rating)
        await db.commit()
        return rating

    @staticmethod
    async def update(rating_id: int, rating: int, db: AsyncSession) -> ImageRating:
        """
        The update function updates a rating in the database.
            Args:
                rating_id (int): The id of the rating to update.
                rating (int): The new value for the image's score.

        :param rating_id: int: Get the rating by id
        :param rating: int: Pass the rating value to be updated
        :param db: AsyncSession: Pass the database session to the function
        :return: A rating object
        """
        rating = await ImageRatingService.get_rating_by_id(rating_id, db)
        if not rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
        rating.rating = rating
        await db.commit()
        return rating
