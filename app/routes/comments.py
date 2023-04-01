from typing import List

from fastapi import HTTPException, status
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.database.models import Comment, UserRole, User
from app.schemas.comment import CommentBase, CommentResponse, CommentUpdate
from app.database.models.image_comments import Comment
from app.repository import comments as repository_comments
from app.utils.filter import UserRoleFilter
from app.services.auth import auth_service


router = APIRouter(prefix='/users/comments', tags=["comments"])


@router.post("/", response_model=CommentResponse,
             dependencies=[Depends(UserRoleFilter(role=UserRole.moderator))])
async def create_comment(body: CommentBase, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Comment:
    """
    The create_comment function creates a new comment in the database.

    :param body: CommentBase: Get the body of the comment
    :param db: AsyncSession: Pass the database session to the repository
    :param current_user: User: Get the user who is currently logged in
    :return: A comment object
    """
    comment = await repository_comments.create_comment(current_user, body, db)

    return comment


@router.get('/', response_model=List[CommentResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60)), Depends(UserRoleFilter(role=UserRole.moderator))])
async def get_comments_by_image_and_user_id(image_id: int,
                                            user_id: int,
                                            skip: int = 0,
                                            limit: int = 10, db: AsyncSession = Depends(get_db),
                                            current_user: User = Depends(auth_service.get_current_user)) -> List[Comment]:
    """
    The get_comments_by_image_and_user_id function returns a list of comments for the specified image and user.

    :param image_id: int: Specify the image_id of the image that we want to get comments for
    :param user_id: int: Get the comments of a specific user
    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments returned
    :param db: AsyncSession: Get the database session from the dependency injection container
    :param current_user: User: Ensure that the user is logged in
    :return: A list of comments
    """
    if user_id is None or image_id is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "Both user_id and image_id must be provided")

    comments = await repository_comments.get_comments_by_image_and_user_id(current_user, image_id, user_id, skip, limit, db)

    return comments


#TODO moderator -> cannot see one comment, but can see the list of comments, if you chose by image_id & user_id
#TODO user -> cannot do anythin else except create a comment
@router.get("/{comment_id}", response_model=CommentResponse,
            dependencies=[Depends(UserRoleFilter(role=UserRole.moderator))])
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> Comment:

    """
    The get_comment function returns a comment by its id.

    :param comment_id: int: Get the comment id from the url path
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A comment object
    """
    comment = await repository_comments.get_comment(current_user, comment_id, db)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return comment


#TODO moderator -> cannot access and update other comments, only his
@router.patch("/{comment_id}", response_model=CommentResponse,
              dependencies=[Depends(UserRoleFilter(role=UserRole.moderator))])
async def update_comment(comment_id: int, body: CommentUpdate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Comment:
    """
    The update_comment function updates a comment in the database.
        The function takes an id of the comment to be updated, and a CommentUpdate object containing
        the new values for each field.

    :param comment_id: int: Identify the comment to be deleted
    :param body: CommentUpdate: Pass the new comment body to the function
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The updated comment
    """
    comment = await repository_comments.update_comment(current_user, comment_id, body, db)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    return comment
