from typing import List

from sqlalchemy import or_, update, delete, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.image_comments import Comment
from app.database.models import User
from app.schemas.comment import CommentBase, CommentUpdate


async def create_comment(user: User, body: CommentBase, db: AsyncSession) -> Comment:

    """
    The create_comment function creates a new comment in the database.
        Args:
            user (User): The user who is creating the comment.
            body (CommentBase): The data for the new comment to be created.

    :param user: User: Get the user_id from the user object
    :param body: CommentBase: Pass in the data for the comment
    :param db: AsyncSession: Pass in the database session
    :return: A comment object
    """
    comment = Comment(
            user_id=body.user_id,
            image_id=body.image_id,
            data=body.data
        )
    db.add(comment)

    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments_by_image_and_user_id(user: User, image_id: int, user_id: int, skip: int, limit: int,
                                            db: AsyncSession) -> List[Comment]:
    """
    The get_comments_by_image_and_user_id function returns a list of comments for the given image and user.

    :param user: User: Check if the user is logged in
    :param image_id: int: Specify the image id of the comment
    :param user_id: int: Get the comments of a specific user
    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments returned
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of comments that match the image_id and user_id
    """
    comments = await db.execute(
        select(Comment)
        .where(and_(Comment.image_id == image_id, Comment.user_id == user_id))
        .offset(skip)
        .limit(limit)
    )

    return comments.scalars().all()


async def get_comment(user: User, comment_id: int, db: AsyncSession) -> Comment:

    """
    The get_comment function takes in a user, comment_id, and db session.
    It returns the comment with the given id that belongs to the given user.

    :param user: User: Pass the user object to the function
    :param comment_id: int: Specify the id of the comment that is being retrieved
    :param db: AsyncSession: Pass in the database session
    :return: A comment if the user is authorized to view it, otherwise none
    """
    comment = await db.scalar(select(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)))

    return comment


async def update_comment(user: User, comment_id: int, body: CommentUpdate, db: AsyncSession) -> Comment:

    """
    The update_comment function updates a comment in the database.

    :param user: User: Ensure that the user making the request is authenticated
    :param comment_id: int: Identify the comment to be updated
    :param body: CommentUpdate: Pass the updated comment data to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated comment
    """
    comment = await db.scalar(
            update(Comment)
            .values(data=body.data)
            .where(and_(Comment.id == comment_id, Comment.user_id == user.id))
            .returning(Comment)
        )

    await db.commit()

    await db.refresh(comment)

    return comment
