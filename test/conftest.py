import asyncio

import pytest
from httpx import AsyncClient

from component_factory import get_config, get_migration_service
from model.configuration import Config
from server import app


@pytest.fixture()
async def test_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


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
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def ensure_db_schema() -> None:
    await get_migration_service().migrate()
