from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserRole, User
from app.database.connect import get_db
from app.schemas.tag import TagModel, TagResponse
from app.repository import tags as repository_tags

from app.utils.filter import UserRoleFilter
from app.services.auth import AuthService

router = APIRouter(prefix='/tags', tags=["tags"])


@router.get("/", response_model=list[TagResponse])
async def read_tags(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(AuthService.get_current_user)):
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def read_tag(tag_id: int, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(AuthService.get_current_user)):
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(body: TagModel, tag_id: int, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(AuthService.get_current_user)):
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse,
               dependencies=[Depends(UserRoleFilter(role=UserRole.moderator))])
async def remove_tag(tag_id: int, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(AuthService.get_current_user)):
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
