from http import HTTPStatus

import pytest

from model.responses.image_responses import CreateImageResponse
from model.responses.subscription import SubscriptionHandlerResponse
from model.responses.user import UserHandlerResponse
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio


async def test_get_by_user_email(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    resp = await test_client.get(
        url='/subscriptions/a@gmail.com',
        resp_model=SubscriptionHandlerResponse,
        assert_status=HTTPStatus.NOT_FOUND,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert resp.detail == 'Not Found'
