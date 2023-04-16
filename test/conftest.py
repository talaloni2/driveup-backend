import asyncio
from typing import Generator

import pytest
from httpx import AsyncClient

from component_factory import get_config, get_migration_service
from model.configuration import Config
from server import app
from test.utils.test_client import TestClient


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def config() -> Config:
    original = get_config()
    return Config(
        server_port=8000,
        db_host=original.db_host,
        db_port=original.db_port,
        db_user=original.db_user,
        db_pass=original.db_pass,
    )


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_client(event_loop) -> TestClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield TestClient(client)


@pytest.fixture(scope="session")
async def ensure_db_schema(event_loop) -> None:
    await get_migration_service().migrate()
