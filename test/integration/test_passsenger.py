from http import HTTPStatus
from fastapi import APIRouter, Depends


import pytest

from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient
from service.passenger_service import PassengerService
from component_factory import get_passenger_service


from test.utils.utils import get_random_email

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
    assert hasattr(resp, "order_id")


async def test_get_drive(test_client: TestClient):

    resp = await test_client.get(
        url="/passenger/get-drive/1",
        resp_model=GetDriveResponse,
    )
    assert hasattr(resp, "drive_id")


