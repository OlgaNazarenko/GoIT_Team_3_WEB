from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class ImageResponse(ImageModel):
    id: int
    detail: str = "Image successfully created"
    
    class Config:
        orm_mode = True


class ImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str
    description: str
    created_at: str
    user_id: str


class ImagePublic(DateTimeModelMixin, ImageBase,  )