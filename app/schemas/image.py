from typing import Optional

from pydantic import Field, validator

from .core import CoreModel, IDModelMixin, DateTimeModelMixin
from app.services.cloudinary import CroppingOrResizingTransformation, formatting_image


class ImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str = Field(..., alias='public_id')
    description: str
    user_id: int

    @validator('url', pre=True, allow_reuse=True)
    def format_url(cls, public_id: str):
        return formatting_image(public_id)['url']


class ImagePublic(DateTimeModelMixin, ImageBase, IDModelMixin):
    class Config:
        orm_mode = True


class ImageCreateResponse(CoreModel):
    image: ImagePublic
    detail: str = "Image successfully uploaded"


class ImageTransformation(CoreModel):
    """
    Model representing the complete transformation parameters for an image

    When changing the dimensions of an uploaded image by setting the image's height, width, and/or aspect ratio,
    you need to decide how to resize or crop the image to fit into the requested size. Use the c (crop/resize) parameter
    for selecting the crop/resize mode.
    """
    image_id: int
    transformation: Optional[CroppingOrResizingTransformation] = None


class FormattedImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str = Field(..., alias="format")


class FormattedImagePublic(DateTimeModelMixin, FormattedImageBase, IDModelMixin):
    class Config:
        orm_mode = True


class FormattedImageCreateResponse(CoreModel):
    original_image_id: int
    formatted_image: FormattedImagePublic
    detail: str = "Image successfully formatted"


class ImageFormatsResponse(CoreModel):
    original_image: ImagePublic
    formatted_images: list[FormattedImagePublic]


class ImageTransformationResponse(CoreModel):
    original_image: ImagePublic
    formatted_image: FormattedImagePublic
