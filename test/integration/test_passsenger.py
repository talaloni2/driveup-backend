from http import HTTPStatus
from fastapi import APIRouter, Depends


import pytest

from model.requests.passenger import PassengerDriveOrderRequest, Address, PassengerGetDrive
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient
from service.passenger_service import PassengerService
from component_factory import get_passenger_service


from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
ADDRESS1 = Address(lon=1, lat=1)
ADDRESS2 = Address(lon=2, lat=2)
ORDER_ID = 1



async def test_post_add_drive_order(test_client: TestClient):
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

    # order_new_drive_request = PassengerDriveOrderRequest(
    #     email=EMAIL,
    #     passengers_amount=PASSENGER_AMOUNT,
    #     source_location=ADDRESS1,
    #     dest_location=ADDRESS2
    # )
    # resp = await test_client.post(
    #     url="/passenger/order-drive",
    #     req_body=order_new_drive_request,
    #     resp_model=DriveOrderResponse,
    # )
    # order_id = resp.order_id

    # passenger_service: PassengerService = Depends(get_passenger_service)
    # await passenger_service.set_status_to_drive_order(order_id=order_id, new_status="ACTIVE")

    getDriveRequest = PassengerGetDrive(
        email=EMAIL,
        order_id=ORDER_ID
    )
    resp = await test_client.post(
        url="passenger/get-drive",
        req_body=getDriveRequest,
        resp_model=GetDriveResponse,
    )
    assert hasattr(resp, "drive_id")


