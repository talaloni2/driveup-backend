from http import HTTPStatus
from fastapi import APIRouter, Depends


import pytest

from model.requests.driver import DriverRequestDrive,DriverAcceptDrive, DriverRejectDrive
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from test.utils.test_client import TestClient
from service.passenger_service import PassengerService
from component_factory import get_passenger_service


from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
CURRENT_LAT = 1
CURRENT_LON = 1
ORDER_ID = 1


async def test_post_request_drive(test_client: TestClient):
    request_drive_request = DriverRequestDrive(
        email=EMAIL,
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        #resp_model=DriveOrderResponse,
    )
    assert hasattr(resp, "order_id")


async def test_accept_drive(test_client: TestClient):
    request_drive_request = DriverRequestDrive(
        email=EMAIL,
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        #resp_model=DriveOrderResponse,
    )
    assert hasattr(resp, "order_id")





