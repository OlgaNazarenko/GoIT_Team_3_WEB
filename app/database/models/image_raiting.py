from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .users import User
from .images import Image


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
