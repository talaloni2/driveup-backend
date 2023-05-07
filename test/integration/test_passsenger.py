from http import HTTPStatus

import pytest

from model.requests.passenger import PassengerDriveOrderRequest, Address, PassengerGetDrive
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

USER_ID = 1
PASSENGER_AMOUNT = 1
ADDRESS1 = Address(1, 1)
ADDRESS2 = Address(2, 2)
ORDER_ID = 1



async def test_post_add_drive_order(test_client: TestClient):
    token = await test_client.get_token()
    order_new_drive_request = PassengerDriveOrderRequest(
        user_id=USER_ID,
        passengers_amount=PASSENGER_AMOUNT,
        source_location=ADDRESS1,
        dest_location=ADDRESS2
    )
    resp = await test_client.post(
        url="/passenger-order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert hasattr(resp, "order_id")


async def test_get_drive(test_client: TestClient):
    token = await test_client.get_token()
    rating_request = PassengerGetDrive(
        user_id=USER_ID,
        order_id=ORDER_ID
    )
    resp = await test_client.get(
        url="/passenger-get-drive",
        req_body=rating_request,
        resp_model=GetDriveResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert hasattr(resp, "order_id")


