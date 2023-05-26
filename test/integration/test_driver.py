import pytest

from model.requests.driver import DriverRequestDrive
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.knapsack import SuggestedSolution
from model.responses.passenger import DriveOrderResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
CURRENT_LAT = 1
CURRENT_LON = 1
ORDER_ID = 1


async def test_post_request_drive(test_client: TestClient, ensure_db_schema: None):
    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
        limits={},
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
    )
    resp_json = resp.json()
    assert "time" in resp_json
    assert "solutions" in resp_json


async def test_accept_drive(test_client: TestClient, ensure_db_schema: None):
    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
    )
    assert resp.status_code == 200


async def test_request_drives_suggestion_already_exists(test_client):
    parameter = DriveOrderRequestParam(
        currentUserEmail=get_random_email(),
        startLat=2,
        startLon=2,
        destinationLat=3,
        destinationLon=3,
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
        limits={},
    )
    first_resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    second_resp = await test_client.post(
        url="/driver/request-drives?force_reject=false",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert len(first_resp.solutions) > 0
    assert first_resp == second_resp


