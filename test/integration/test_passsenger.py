from http import HTTPStatus

import pytest

from model.requests.passenger import PassengerDriveOrderRequest, Address, PassengerGetDrive
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
ADDRESS1 = Address(lon=1, lat=1)
ADDRESS2 = Address(lon=2, lat=2)
ORDER_ID = 1



async def test_post_add_drive_order(test_client: TestClient):
    #token = await test_client.get_token()
    order_new_drive_request = PassengerDriveOrderRequest(
        email=EMAIL,
        passengers_amount=PASSENGER_AMOUNT,
        source_location=ADDRESS1,
        dest_location=ADDRESS2
    )
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    assert hasattr(resp, "order_id")


async def test_get_drive(test_client: TestClient):
    token = await test_client.get_token()
    rating_request = PassengerGetDrive(
        email=EMAIL,
        order_id=ORDER_ID
    )
    resp = await test_client.get(
        url="/passenger-get-drive",
        req_body=rating_request,
        resp_model=GetDriveResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert hasattr(resp, "order_id")


