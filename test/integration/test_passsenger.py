from http import HTTPStatus

import pytest

from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
ADDRESS1_lat = 1
ADDRESS1_lon  =1
ADDRESS2_lat = 2
ADDRESS2_lon =2
ORDER_ID = 1


async def test_post_add_drive_order(test_client: TestClient):
    parameter = DriveOrderRequestParam(
        currentUserEmail = EMAIL,
        startLat= ADDRESS1_lat,
        startLon= ADDRESS1_lon,
        destinationLat= ADDRESS2_lat,
        destinationLon= ADDRESS2_lon,
        numberOfPassengers= 1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(
        parameter=parameter
    )
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    assert resp.order_id > 0
    assert resp.estimated_cost > 0


async def test_get_drive(test_client: TestClient):
    parameter = DriveOrderRequestParam(
        currentUserEmail=EMAIL,
        startLat=ADDRESS1_lat,
        startLon=ADDRESS1_lon,
        destinationLat=ADDRESS2_lat,
        destinationLon=ADDRESS2_lon,
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(
        parameter=parameter
    )
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    await test_client.get(
        url=f"/passenger/get-drive/{resp.order_id}",
        resp_model=GetDriveResponse,
    )


async def test_get_non_existing_drive(test_client: TestClient):
    await test_client.get(
        url=f"/passenger/get-drive/{pow(2, 30)}",
        assert_status=HTTPStatus.NOT_FOUND,
    )
