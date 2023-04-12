import sys
import os

# add parent directory of app to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest import mock
import unittest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import configure_mappers
import sqlalchemy as sa


from app.repository.tags import get_or_create_tags
from app.database.models.images import Image
from app.database.models import Tag
from app.repository.images import (
    get_image_by_id,
    create_image,
    update_description,
    delete_image,
    get_images,
)


class TestImages(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = dict(
            id=1,
            public_id='1',
            description="Something to be written",
            user_id=2,
            tags=['today','Seoul']
        )

    def setUp(self) -> None:
        self.session = MagicMock(spec=AsyncSession)
        self.image_id = 2


    async def test_get_image_by_id(self):
        image_mock = Mock(spec=Image)
        self.session.scalar.return_value = image_mock

        result = await get_image_by_id(self.image_id, self.session)

        self.assertEqual(result, image_mock)

# to write create_image, update_description, get_images

    async def test_delete_image(self):
        mock_image = Mock(spec=Image)
        mock_image.id = 1

        self.session.scalar.return_value = mock_image

        await delete_image(mock_image, self.session)

        self.session.delete.assert_called_once_with(mock_image)
        self.session.commit.assert_called_once()

    async def test_delete_image_not_found(self):
        self.session.scalar.return_value = None

        await delete_image(image=Image(id=1), db=self.session)

        self.assertTrue(self.session.commit.called)


if __name__ == '__main__':
    unittest.main()
