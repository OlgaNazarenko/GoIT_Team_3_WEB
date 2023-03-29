import uuid
from typing import BinaryIO

import cloudinary
from cloudinary.api import resource
from cloudinary.uploader import upload

from config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


def upload_image(file: BinaryIO) -> str:
    """
    The upload_image function takes a file object and uploads it to Cloudinary.
    It returns the public ID of the uploaded image.

    :param file: BinaryIO: Pass the file to be uploaded
    :return: A string
    """
    file_id = settings.cloudinary_folder + uuid.uuid4().hex

    upload(file, public_id=file_id, owerwrite=True)

    return file_id


def get_format_image(file_id: str, width: int = 250, height: int = 250, crop: str = 'fill'):
    return cloudinary.CloudinaryImage(file_id).build_url(
        width=width,
        height=height,
        crop=crop,
        version=resource(file_id)['version']
    )
