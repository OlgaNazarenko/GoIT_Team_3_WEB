from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .users import User
from .images import Image


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(500), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"))
    image_id: Mapped[str] = mapped_column(ForeignKey(Image.id, ondelete="CASCADE", onupdate="CASCADE"))

    user: Mapped[User] = relationship(backref="comments")
    image: Mapped[Image] = relationship(backref="comments")
