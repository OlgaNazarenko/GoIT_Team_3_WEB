from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, Date, String, Boolean, func, Table, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, mapped_column, Mapped
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime


Base = declarative_base()

image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    user_role: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255))
    confirmed: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class Image(Base):
    __tablename__ = 'images'
    __table_args__ = (
        UniqueConstraint('user_id', name='unique_contact_user'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    user: Mapped[User] = relationship(backref="images")
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    image_id: Mapped[str] = mapped_column(ForeignKey(Image.id, ondelete="CASCADE"))

    user: Mapped[User] = relationship(backref="comments")
    image: Mapped[Image] = relationship(backref="comments")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
