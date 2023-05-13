from http import HTTPStatus

import pytest

from model.responses.image_responses import CreateImageResponse
from model.responses.user import UserHandlerResponse
from model.user_schemas import RequestUser, UserSchema
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio

EMAIL = "a@gmail.com"
PASSWORD = "Aa111111"


async def get_token(test_client: TestClient):
    try:
        resp = await test_client.post(
            url="/users/",
            req_body=RequestUser(
                parameter=UserSchema(
                    car_color="Black",
                    car_model="Hatzil",
                    email=EMAIL,
                    full_name="Dov Sherman",
                    password=PASSWORD,
                    phone_number="0541112222",
                    plate_number="0000000",
                )
            ),
            resp_model=UserHandlerResponse,
            assert_status=None,
        )
        print(resp)
    except Exception as e:
        print(e)
    return (
        await test_client.post(
            url="/token",
            req_body=None,
            resp_model=None,
            data={"username": EMAIL, "password": PASSWORD},
        )
    ).json()["access_token"]


async def test_create_with_login(test_client: TestClient, ensure_db_schema: None):
    token = await get_token(test_client)
    assert token is not None


async def test_validate_user(test_client: TestClient, ensure_db_schema: None):
    token = await get_token(test_client)
    resp = await test_client.get(
        url="/users/validate_token",
        resp_model=UserHandlerResponse,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.code == 200
    assert resp.result == {"is_valid": True, "token": {"email": EMAIL}}
