import pytest

from model.responses.user import UserHandlerResponse
from model.user_schemas import RequestUser, UserSchema
from test.utils.test_client import TestClient
from test.utils.utils import get_random_string

pytestmark = pytest.mark.asyncio


async def test_create_login_get_update_delete(test_client_unauthenticated: TestClient, ensure_db_schema: None):
    test_client = test_client_unauthenticated
    new_username = f"test_user_{get_random_string()}@gmail.com"
    token = (await test_client.post(
        url="/users/",
        req_body=RequestUser(parameter=UserSchema(
            email=new_username,
            password="1234",
            phone_number=get_random_string(),
            full_name=get_random_string(),
        )),
        resp_model=UserHandlerResponse
    )).result["token"]
    assert (await test_client.get(
        url=f'/users/{new_username}',
        resp_model=UserHandlerResponse,
        headers={"Authorization": f"Bearer {token}"}
    )) == UserHandlerResponse(code=200, status='OK', message='User fetched successfully', result={'email': new_username, 'phone_number': '0542583838', 'car_model': 'Hatzil', 'plate_number': '0000000', 'full_name': 'Dov Sherman', 'car_color': 'Black'}, detail=None)
    assert (await test_client.put(
        url='/users/user_for_test@gmail.com',
        req_body=RequestUser(parameter=UserSchema(
            full_name="Tznon Metoonaf"
        )),
        resp_model=UserHandlerResponse,
    )) == UserHandlerResponse(code=200, status='OK', message='User updated successfully', result={'email': 'user_for_test@gmail.com', 'password': 'Aa111111', 'phone_number': '0542583838', 'car_model': 'Hatzil', 'plate_number': '0000000', 'token': '094ebeb0-a7be-5653-9752-16a1b22c688a', 'full_name': 'Tznon Metoonaf', 'car_color': 'Black'}, detail=None)
    assert (await test_client.delete(
        url='/users/user_for_test@gmail.com',
        resp_model=UserHandlerResponse,
    )) == UserHandlerResponse(code=200, status='OK', message='User deleted successfully', result=None, detail=None)


async def test_validate_user(test_client_unauthenticated: TestClient, ensure_db_schema: None):
    test_client = test_client_unauthenticated
    new_username = f"test_user_{get_random_string()}@gmail.com"
    token = (await test_client.post(
        url="/users/",
        req_body=RequestUser(parameter=UserSchema(
            email=new_username,
            password="1234",
            phone_number=get_random_string(),
            full_name=get_random_string(),
        )),
        resp_model=UserHandlerResponse
    )).result["token"]
    resp = await test_client.get(
        url='/users/validate_token',
        resp_model=UserHandlerResponse,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.code == 200
    # assert resp.result == {"is_valid": True}
