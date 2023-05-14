from http import HTTPStatus

import pytest

from model.requests.subscription import SubscriptionHandlerCreateUserSubscriptionMapRequest
from model.responses.image_responses import CreateImageResponse
from model.responses.subscription import SubscriptionHandlerResponse
from model.responses.user import UserHandlerResponse
from model.user_subscription_map_schemas import RequestUserSubscriptionMap
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio


async def test_get_user_subscription_maps(test_client: TestClient, ensure_db_schema: None):
    resp = await test_client.get(
        url='/user_subscription_maps/',
        resp_model=SubscriptionHandlerResponse,
    )
    assert isinstance(resp.result, list)


async def test_create_get_delete_user_subscription_map(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    assert (await test_client.post(
        url='/user_subscription_maps/',
        req_body=RequestUserSubscriptionMap(**{
            "parameter": {
                "subscription_name": "Basic",
                "user_email": "user_for_test@gmail.com",
                "card_owner_id": "string",
                "card_number": "string",
                "cvv": "string"
            }
        }),
        resp_model=SubscriptionHandlerResponse,
        headers={'Authorization': f"Bearer {token}"},
    )) == SubscriptionHandlerResponse(code=200, status='OK', message='UserSubscriptionMap created successfully', result=None, detail=None)

    response = await test_client.get(
        url='/user_subscription_maps/user_for_test@gmail.com/Basic',
        resp_model=SubscriptionHandlerResponse,
        assert_status=HTTPStatus.OK,
        headers={'Authorization': f"Bearer {token}"},
    )
    del response.result["expiration_date"]
    del response.result["start_date"]
    assert response == SubscriptionHandlerResponse(code=200, status='OK', message='UserSubscriptionMap fetched successfully', result={'card_owner_id': 'string', 'cvv': 'string', 'user_email': 'user_for_test@gmail.com', 'card_number': 'string', 'subscription_name': 'Basic'}, detail=None)

    response = await test_client.get(
        url='/users_map/user_for_test@gmail.com',
        resp_model=SubscriptionHandlerResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    del response.result[0]["expiration_date"]
    del response.result[0]["start_date"]
    assert response == SubscriptionHandlerResponse(code=200, status='OK', message='UserSubscriptionMap fetched successfully', result=[{'card_owner_id': 'string', 'cvv': 'string', 'user_email': 'user_for_test@gmail.com', 'card_number': 'string', 'subscription_name': 'Basic'}], detail=None)

    assert (await test_client.delete(
        url='/user_subscription_maps/user_for_test@gmail.com/Basic',
        resp_model=SubscriptionHandlerResponse,
        headers={'Authorization': f"Bearer {token}"},
    )) == SubscriptionHandlerResponse(code=200, status='OK', message='UserSubscriptionMap deleted successfully', result=None, detail=None)


async def test_get_by_user_email(test_client: TestClient, ensure_db_schema: None):
    resp = await test_client.get(
        url="/users_map/user_for_test@gmail.com",
        resp_model=SubscriptionHandlerResponse,
    )
    assert resp.detail == "No subscriptions for this user."
