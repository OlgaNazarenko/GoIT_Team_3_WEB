from fastapi import HTTPException, status
from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .users import User
from .images import Image
from app.services.auth import role_required


class ImageRating(Base):
    __tablename__ = "image_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"))
    image_id: Mapped[int] = mapped_column(ForeignKey(Image.id, ondelete="CASCADE", onupdate="CASCADE"))
    rating: Mapped[int] = mapped_column(CheckConstraint("rating >= 1 AND rating <= 5"))

    user: Mapped[User] = relationship("User", backref="image_ratings")
    image: Mapped[Image] = relationship("Image", backref="image_ratings")

    __table_args__ = (
        UniqueConstraint('user_id', 'image_id', name='unique_user_image_rating'),
        CheckConstraint("user_id != image.user_id", name='user_cannot_rate_own_image')
    )

    @classmethod
    @role_required('admin', 'moderator')
    async def delete_rating(cls, db_session, rating_id: int):
        """
        The delete_rating function deletes a rating from the database.
            Args:
                db_session (Session): The SQLAlchemy session object.
                rating_id (int): The ID of the image to delete.
        :param cls: Pass the class of the object that is being deleted
        :param db_session: Access the database
        :param rating_id: int: Find the rating in the database
        :return: The rating that was deleted
        :doc-author: Trelent
        """
        rating = await db_session.get(ImageRating, rating_id)
        if not rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
        db_session.delete(rating)
        db_session.commit()
        return rating

    @classmethod
    async def get_all_ratings(cls, db_session, image_id: int):
        """
        The get_all_ratings function returns all ratings for a given image.
        :param cls: Refer to the class itself
        :param db_session: Pass the database session to the function
        :param image_id: int: Select the image id from the database
        :return: All the ratings of a given image
        :doc-author: Trelent
        """
        ratings = await db_session.execute(
            cls.__table__.select().where(cls.image_id == image_id)
        )
        return ratings.fetchall()

    @staticmethod
    async def get_rating_by_id(db: AsyncSession, rating_id: int):
        rating = await db.query(ImageRating).filter(ImageRating.id == rating_id).first()
        return rating

    @classmethod
    async def delete_rating_by_id(cls, db_session, rating_id: int):
        rating = await cls.get_rating_by_id(db_session, rating_id)
        if rating:
            await db_session.delete(rating)
            await db_session.commit()
            return True
        return False

    @classmethod
    async def create(cls, db: AsyncSession, rating: int, image_id: int, user_id: int):
        rating = cls(rating=rating, image_id=image_id, user_id=user_id)
        db.add(rating)
        await db.commit()
        await db.refresh(rating)
        return rating

    async def update(self, db_session, rating: int, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.rating = rating
        await db_session.flush()
        return self
