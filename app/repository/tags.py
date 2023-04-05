from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Tag
from app.schemas.tag import TagBase


async def get_tags(skip: int, limit: int, db: AsyncSession) -> list[Tag]:
    tags = await db.scalars(
        select(Tag)
        .offset(skip)
        .limit(limit)
    )

    return tags.all()  # noqa


async def get_tags_by_list_values(values: list[str], db: AsyncSession) -> list[Tag]:
    tags = await db.scalars(
        select(Tag)
        .filter(Tag.name.in_(values))
    )
    return tags.all()  # noqa


async def get_tag_by_id(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    return await db.scalar(select(Tag).filter(Tag.id == tag_id))


async def get_or_create_tags(values: list[str], db: AsyncSession) -> list[Tag]:
    tags = await get_tags_by_list_values(values, db)
    new_tags = []

    for value in values:
        for tag in tags:
            if value == tag.name:
                break
        else:
            new_tags.append(Tag(name=value.strip()))

    db.add_all(new_tags)

    await db.commit()
    for new_tag in new_tags:
        await db.refresh(new_tag)

    tags.extend(new_tags)

    return tags


async def update_tag(tag_id: int, body: TagBase, db: AsyncSession) -> Tag | None:
    tag = await db.scalar(select(Tag).filter(Tag.id == tag_id))
    if tag:
        tag.name = body.name
        await db.commit()

        await db.refresh(tag)

    return tag


async def remove_tag(tag_id: int, db: AsyncSession) -> Tag | None:
    tag = await db.scalar(select(Tag).filter(Tag.id == tag_id))
    if tag:
        await db.delete(tag)
        await db.commit()

    return tag
