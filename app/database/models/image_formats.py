from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base
from .users import User
from .images import Image


class ImageFormat(Base):
    __tablename__ = "image_formats"
    __table_args__ = (
        UniqueConstraint('format', 'image_id', name='unique_format_image'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    format: Mapped[dict] = mapped_column(JSONB)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"), index=True)
    image_id: Mapped[str] = mapped_column(ForeignKey(Image.id, ondelete="CASCADE", onupdate="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())

    user: Mapped[User] = relationship(backref="formats")
    image: Mapped[Image] = relationship(backref="formats")
