import pytest

from model.responses.image_responses import CreateImageResponse
from model.responses.user import UserHandlerResponse, GetUserByEmailResponse, GetUserByEmailResult
from model.user_schemas import RequestUser, UserSchema
from test.utils.utils import get_random_string

pytestmark = pytest.mark.asyncio


async def test_create_login_get_update_delete(test_client, unauthenticated, ensure_db_schema: None):
    new_username = f"test_user_{get_random_string()}@gmail.com"
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
    response = await test_client.get(
        url=f"/users/{new_username}", resp_model=GetUserByEmailResponse, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.result == GetUserByEmailResult(
        full_name=new_username,
        email=new_username,
        car_color=None,
        phone_number=new_username,
        car_model=None,
        plate_number=None,
    )
    response = await test_client.put(
        url=f"/users/update",
        req_body=RequestUser(parameter=UserSchema(full_name="Tznon Metoonaf")),
        resp_model=UserHandlerResponse,
        headers={"Authorization": f"Bearer {token}"},
    )
    del response.result["password"]
    assert response == UserHandlerResponse(
        code=200,
        status="OK",
        message="User updated successfully",
        result={
            "full_name": "Tznon Metoonaf",
            "email": new_username,
            "car_color": None,
            "phone_number": new_username,
            "car_model": None,
            "plate_number": None,
        },
        detail=None,
    )
    assert (
        await test_client.delete(
            url="/users/delete", resp_model=UserHandlerResponse, headers={"Authorization": f"Bearer {token}"}
        )
    ) == UserHandlerResponse(code=200, status="OK", message="User deleted successfully", result=None, detail=None)


async def test_validate_user(test_user, test_client, ensure_db_schema: None):
    token, new_username = test_user.token, test_user.email
    resp = await test_client.get(
        url="/users/validate_token", resp_model=UserHandlerResponse, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.code == 200
    # assert resp.result == {"is_valid": True}


async def test_get_user_with_image(test_client, test_user, ensure_db_schema: None):
    token, new_username = test_user.token, test_user.email
    with open("test/resources/image-upload.png", mode="rb") as f:
        image_resp = await test_client.post(
            url="/images/upload",
            req_body=None,
            resp_model=CreateImageResponse,
            files={"image": ("Charmander", f)},
            headers={"Authorization": f"Bearer {token}"},
        )

    user_response = await test_client.get(
        url=f"/users/{new_username}", resp_model=GetUserByEmailResponse, headers={"Authorization": f"Bearer {token}"}
    )

    assert user_response.result.image_url == f"/images/{image_resp.id}"

    await test_client.get(f"/images/{image_resp.id}", headers={"Authorization": f"Bearer {token}"})
