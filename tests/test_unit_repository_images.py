import sys
import os

# add parent directory of app to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

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
            tags=['today', 'Seoul']
        )

    def setUp(self) -> None:
        super().setUp()
        self.session = MagicMock(spec=AsyncSession)
        self.image_id = 2

    async def test_get_image_by_id(self):
        image_mock = Mock(spec=Image)
        self.session.scalar.return_value = image_mock

        result = await get_image_by_id(self.image_id, self.session)

        self.assertEqual(result, image_mock)

    async def test_create_image(self):
        image_data = {
            'user_id': self.image['user_id'],
            'description': self.image['description'],
            'public_id': self.image['public_id']
        }

        image = Image(**image_data)
        tag1 = Tag(name=self.image['tags'][0])
        tag2 = Tag(name=self.image['tags'][1])
        expected_tags = [tag1, tag2]

        get_tags_mock = MagicMock(return_value=expected_tags)
        get_or_create_mock = MagicMock(return_value=expected_tags)
        self.session.scalars.return_value = MagicMock(all=MagicMock(return_value=expected_tags))

        result = await create_image(self.image['user_id'], self.image['description'], self.image['tags'],
                                    self.image['public_id'], self.session)

        self.assertEqual(result.user_id, image.user_id)
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.public_id, image.public_id)
        self.assertEqual(result.tags, expected_tags)

    async def test_update_description(self):
        image_data = {
            'id': self.image['id'],
            'user_id': self.image['user_id'],
            'description': self.image['description'],
            'public_id': self.image['public_id']
        }

        image = Image(**image_data)
        tag1 = Tag(name=self.image['tags'][0])
        tag2 = Tag(name=self.image['tags'][1])
        expected_tags = [tag1, tag2]

        expected_image = Image(id=self.image['id'], user_id=self.image['user_id'],
                               description='new description',
                               public_id=self.image['public_id'])
        get_image_by_id_mock = MagicMock(return_value=expected_image)
        self.session.scalars.return_value = MagicMock(all=MagicMock(return_value=expected_tags))

        result = await update_description(
            self.image['id'],
            self.image['description'],
            self.image['tags'],
            self.session
        )

        id_mock = AsyncMock(return_value=image.id)
        result.id = id_mock
        id_result = await result.id()

        self.assertEqual(id_result, image.id)
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.tags, expected_tags)

    async def test_get_images(self):
        image_mock = Mock(spec=Image)
        self.session.scalars.return_value = [image_mock]

        result = await get_images(skip=0, limit=10, description='Test', tags=['test'], image_id=1, user_id=1,
                                  db=self.session)

        self.assertEqual(result[0].id, image_mock.id)
        self.assertEqual(result[0].description, image_mock.description)
        self.assertEqual(result[0].user_id, image_mock.user_id)
        self.assertEqual(result[0].tags, image_mock.tags)
        self.session.scalars.assert_called_once()

    async def test_delete_image(self):
        mock_image = Mock(spec=Image)
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
