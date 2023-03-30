from fastapi import APIRouter

from . import auth
from . import users
from . import images


router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(images.router)

__all__ = (
    'router',
)
