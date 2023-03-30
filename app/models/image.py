from pydantic import BaseModel, Field


class ImageModel(BaseModel):
    description: str = Field(min_length=1, max_length=1200)


class ImageResponse(ImageModel):
    id: int
    detail: str = "Image successfully created"
    
    class Config:
        orm_mode = True