from pytest import mark

from fastapi import status


@mark.asyncio
class TestUploadImage:
    url_path = "api/images/"

    @mark.usefixtures('mock_rate_limit')
    @mark.parametrize(
        "status_code, detail, authorization, type_",
        (
                (status.HTTP_401_UNAUTHORIZED, "Not authenticated", None, None),
                (status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", "invalid", None),
                (status.HTTP_422_UNPROCESSABLE_ENTITY, "Maximum five tags can be added", "valid", "invalid_count_tags"),
                (status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid length tag: ta", "valid", "invalid_length_tag"),
                (status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid image file", "valid", None),
        )
    )
    async def test_exceptions(self, client, access_token, user, mocker,
                              status_code, detail, authorization, type_):
        mocker.patch("app.services.cloudinary.upload_image", return_value=None)

        if authorization == "invalid":
            headers = {"Authorization": "Bearer invalid_access_token"}
        elif authorization == "valid":
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}

        data = {
            "description": "Image description.",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
        }

        if type_ == "invalid_count_tags":
            data['tags'] += 'tag6'
        elif type_ == "invalid_length_tag":
            data['tags'] = ['ta']

        response = client.post(
            self.url_path,
            headers=headers,
            files={"file": ("test.png", b"image", "image/png")},
            data=data
        )

        assert response.status_code == status_code
        assert response.json()['detail'] == detail

    @mark.usefixtures('mock_rate_limit')
    async def test_was_successfully(self, client, access_token, user, mocker):
        mock_image = {
            "url": "https://res.cloudinary.com/dlwnuqx3p/image/upload/cld-sample-5",
            "public_id": "cld-sample-5",
            "version": "1678785308"
        }
        mocker.patch("app.services.cloudinary.upload_image", return_value=mock_image)

        response = client.post(
            self.url_path,
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("test.png", b"image", "image/png")},
            data={"description": "Image description."}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['message'] == "Image successfully uploaded"
        assert response.json()['image']['url'] == mock_image['url']
