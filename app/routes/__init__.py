from fastapi import APIRouter

from . import auth
from . import users


router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)


__all__ = (
    'router',
)
