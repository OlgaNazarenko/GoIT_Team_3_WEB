from fastapi import APIRouter

from . import auth
from . import users
from . import images
from . import comments


router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(images.router)
router.include_router(comments.router)

__all__ = (
    'router',
)
