from pydantic import BaseModel
from typing import Optional


class ImageRatingCreate(BaseModel):
    user_id: int
    image_id: int
    rating: int


class ImageRatingUpdate(BaseModel):
    rating: Optional[int] = None

    class Config:
        orm_mode = True
