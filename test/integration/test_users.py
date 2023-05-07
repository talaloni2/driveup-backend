from http import HTTPStatus

import pytest

from model.responses.image_responses import CreateImageResponse
from model.responses.user import UserHandlerResponse
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio


async def test_create_with_login(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    assert token == 'f7948d51-613c-5301-9d98-a741bbb7f8ed'


async def test_validate_user(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    resp = await test_client.get(
        url='/users/validate_token',
        resp_model=UserHandlerResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert resp.code == 200
    assert resp.result == {"is_valid": True}
