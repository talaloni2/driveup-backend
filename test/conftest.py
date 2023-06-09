import asyncio
from typing import Generator, NamedTuple
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from component_factory import (
    get_config,
    get_migration_service,
    get_directions_service,
    get_db_session_maker,
    create_db_engine,
    get_database_url,
    get_passenger_service,
    get_driver_service,
)
from controllers.utils import AuthenticatedUser, authenticated_user
from model.configuration import Config
from model.responses.directions_api import DirectionsApiResponse
from model.responses.user import UserHandlerResponse
from model.user_schemas import RequestUser, UserSchema
from server import app
from service.directions_service import DirectionsService
from test.utils.test_client import TestClient
from test.utils.utils import get_random_string, get_random_email


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
        knapsack_service_url=original.knapsack_service_url,
        geocoding_api_key=original.geocoding_api_key,
        directions_api_url="MOCK",
        db_url=None,
        subscriptions_handler_base_url="MOCK",
        users_handler_base_url="MOCK",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def _create_new_user_get_token(test_client: TestClient, new_username: str) -> tuple[str, str]:
    user = (
        await test_client.post(
            url="/users/",
            req_body=RequestUser(
                parameter=UserSchema(
                    email=new_username,
                    password="1234",
                    phone_number=new_username,
                    full_name=new_username,
                )
            ),
            resp_model=UserHandlerResponse,
        )
    )
    return user.result["token"], new_username


@pytest.fixture
async def test_client(event_loop) -> TestClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        tc = TestClient(client)
        new_user = await _create_new_user_get_token(tc, get_random_email())
        app.dependency_overrides[authenticated_user] = lambda: AuthenticatedUser(email=new_user[1], token=new_user[0])
        yield tc

    if authenticated_user in app.dependency_overrides:
        del app.dependency_overrides[authenticated_user]


@pytest.fixture
async def unauthenticated(test_client):
    if authenticated_user in app.dependency_overrides:
        del app.dependency_overrides[authenticated_user]
    return test_client


class TestUser(NamedTuple):
    email: str
    token: str


@pytest.fixture()
async def test_user(unauthenticated, test_client) -> TestUser:
    new_username = f"test_user_{get_random_string()}@g.com"
    token = (
        await test_client.post(
            url="/users/",
            req_body=RequestUser(
                parameter=UserSchema(
                    email=new_username,
                    password="1234",
                    phone_number=new_username,
                    full_name=new_username,
                )
            ),
            resp_model=UserHandlerResponse,
        )
    ).result["token"]
    yield TestUser(email=new_username, token=token)

    await test_client.delete(url="/users/delete", headers={"Authorization": f"Bearer {token}"})


@pytest.fixture()
def authenticated_passenger(test_client):
    app.dependency_overrides[authenticated_user] = """passenger"""


@pytest.fixture(scope="session", autouse=True)
async def ensure_db_schema(event_loop) -> None:
    await get_migration_service().migrate()


@pytest.fixture
async def clear_orders_tables(ensure_db_schema):
    async with get_db_session_maker(create_db_engine(get_database_url(get_config())))() as session:
        async with session.begin():
            await get_passenger_service(session).delete_all_passenger_drive_order()
            await get_driver_service(session).delete_all_driver_drive_orders()
