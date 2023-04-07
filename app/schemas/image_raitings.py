from typing import Optional

from .core import CoreModel


class ImageRatingCreate(CoreModel):
    user_id: int
    image_id: int
    rating: int


class ImageRatingUpdate(CoreModel):
    rating: Optional[int] = None

    class Config:
        orm_mode = True
