import pytest
from pytest import fixture, mark
from fastapi import status
from unittest.mock import MagicMock, patch
from sqlalchemy import select
from sqlalchemy.orm import session

from app.routes.image_comments import create_comment
from app.services.auth import get_current_active_user
from app.database.models.users import User
from app.database.models.image_comments import ImageComment

@fixture()
async def access_token(client, user, new_session_maker, mocker) -> str:
    mocker.patch('app.routes.auth.send_email_confirmed')

    client.post("/api/auth/signup", json=user)

    current_user: User = await new_session_maker.scalar(select(User).filter(User.email == user['email']))
    if current_user is not None:
        current_user.confirmed = True
    new_session_maker.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )

    return response.json()['access_token']


@fixture(scope="module")
def comment() -> dict:
    return {
        "data": "text",
        "user_id": 1,
        "image_id": 2
    }
#
# def test_root(client):
#     res = client.get('/api/healthchecker')
#     print(res.text)
#
#     assert res.status_code == 201
#


class TestCreateComment:
    url_path = "api/images/comments"

    @mark.usefixtures('mock_rate_limit')
    def test_create_comment(self, client, comment, access_token, new_session_maker):

        response = client.post(
            self.url_path,
            json=comment,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"{client=}")

        print(f"{response.text=}")
        print(f"{response.status_code=}")
        assert response.status_code == status.HTTP_201_CREATED, response.text

        assert response.json().get('id') is not None
        assert comment['user_id'] == response.json().get('user_id')
        assert comment['image_id'] == response.json().get('image_id')
        assert comment['data'] == response.json().get('data')

    @mark.usefixtures('mock_rate_limit')
    @mark.parametrize(
        "status_code, detail, authorization",
        (
                (status.HTTP_401_UNAUTHORIZED, "Not authenticated", None),
                (status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", "invalid"),
                (status.HTTP_409_CONFLICT, "A comment with this email address already exists", "valid"),
        )
    )
    def test_create_comment_exceptions(self, client, access_token, comment,
                                       status_code, detail, authorization):
        if authorization == "invalid":
            headers = {"Authorization": "Bearer invalid_access_token"}
        elif authorization == "valid":
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}

        response = client.post(self.url_path, json=comment, headers=headers)

        assert response.status_code == status_code
        assert response.json()['detail'] == detail


class TestGetComment:
    url_path = "api/images/comments/{comment_id}"

    def test_get_comment(self, client, session, access_token):
        comment = ImageComment(data="test comment")
        session.add(comment)
        session.commit()

        response = client.get(
            self.url_path.format(comment_id=comment.id),
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()['id'] == comment.id
        assert response.json(['data']) == comment.data

    @mark.usefixtures('mock_rate_limit')
    def test_get_comment_not_found(self, client, access_token):
        response = client.get(
            self.url_path.format(comment_id=3),
            headers = {"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        data = response.json()
        assert data["id"] == "Not Found"


class TestGetCommentsByIDs:
    url_path = "api/images/comments"

    @mark.usefixtures('mock_rate_limit')
    @pytest.mark.parametrize(
        "user_id, image_id, comment",
        [
            ("1", None, "Some text"),
            (None, "2", "Some text"),
            ("2", "3", "Some text",)
        ]
    )
    def test_get_comments_by_user_or_user_id(self, client, new_session_maker, access_token, comment, user_id, image_id):
        if user_id:
            params = {"user_id": user_id}
        elif image_id:
            params = {"image_id": image_id}

        response = client.get(
            self.url_path,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        if user_id and image_id:
            assert data[0]["user_id"] == comment["user_id"] # noqa
            assert data[0]["image_id"] == comment["image_id"] # noqa
        elif user_id:
            assert all(c["user_id"] == user_id for c in data)
        elif image_id:
            assert all(c["image_id"] == image_id for c in data)


class TestUpdateComment:
    url_path = "api/images/comments"

    def test_update_comment(self, client, comment, access_token, new_session_maker):
        updated_comment = {**comment, "data": "Updated comment"}
        comment.update(
            data=updated_comment,
        )

        response = client.put(
            self.url_path.format(comment_id=2),
            json=updated_comment,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['comment_id'] == comment.id
        assert response.json()['data'] == updated_comment['data']

        db_comment = new_session_maker.execute(select(ImageComment).where(ImageComment.id == comment.id)).scalar_one()
        assert db_comment.data == updated_comment['data']

    def test_update_comment_not_found(self, client, access_token):
        response = client.put(
            self.url_path.format(comment_id=1),
            json={"data": "Updated comment"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["comment_id"] == "Not Found"


# class TestRemoveComment:
#     url_path = "api/images/comments/{comment_id}"
#
#     def test_remove_comment(self, client, access_token, comment):
#         response = client.delete(
#             self.url_path.format(contact_id=1),
#             headers = {"Authorization": f"Bearer {access_token}"}
#         )
#
#         assert response.status_code == status.HTTP_200_OK, response.text
#         assert response.json()["contact_id"] == comment["contact_id"]
#         assert "id" in response.json()
#
#     def test_repeat_delete_comment(self, client, access_token):
#         response = client.delete(
#             self.url_path.format(contact_id=1),
#             headers = {"Authorization": f"Bearer {access_token}"}
#         )
#
#         assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
#         assert response.json()["contact_id"] == "Not Found"
