from fastapi import Depends, HTTPException

from app.database.models import UserRole, User
from app.services.auth import auth_service


class UserRoleFilter:
    def __init__(self, role: UserRole):
        if role not in UserRole:
            raise ValueError(f"Invalid role: {role}")
        self.role = role

    async def __call__(self, current_user: User = Depends(auth_service.get_current_user)):
        if current_user.role == UserRole.admin:
            return

        elif current_user.role == UserRole.moderator and self.role in [UserRole.moderator, UserRole.user]:
            return

        elif current_user.role == UserRole.user and self.role == UserRole.user:
            return

        raise HTTPException(status_code=400, detail="Invalid role")
