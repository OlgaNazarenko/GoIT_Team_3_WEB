import pytest
from fastapi.testclient import TestClient
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from app.database.connect import get_db
from app.database.models import Base
from app.services.auth import AuthService
from config import settings
from main import app

async_engine = create_async_engine(settings.db_url, future=True)


# @pytest.fixture(scope="module")
# async def init_db():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module")
def new_session_maker() -> Session:
    return sessionmaker(async_engine, autocommit=False, autoflush=False, class_=AsyncSession)  # noqa


@pytest.fixture()
def client(new_session_maker) -> TestClient:
    async def override_get_db():
        async with new_session_maker() as session:  # noqa
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="package")
def user() -> dict:
    return {
        "email": "email@test.com",
        "username": "test_user",
        "password": "test_pwd",
        "first_name": "Stepan",
        "last_name": "Giga",
    }


@pytest.fixture(scope="function")
def mock_rate_limit(mocker):
    mock_rate_limit = mocker.patch.object(RateLimiter, '__call__', autospec=True)
    mock_rate_limit.return_value = False


@pytest.fixture(autouse=True)
def mock_auth_redis(mocker):
    mock_redis = mocker.patch.object(AuthService, 'redis', autospec=True)
    mock_redis.get.return_value = None
