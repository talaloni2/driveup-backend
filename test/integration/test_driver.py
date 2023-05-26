from http import HTTPStatus
from fastapi import APIRouter, Depends


import pytest

from model.requests.driver import DriverRequestDrive
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam

from model.responses.passenger import DriveOrderResponse
from model.responses.knapsack import SuggestedSolution
from test.utils.test_client import TestClient


pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
CURRENT_LAT = 1
CURRENT_LON = 1
ORDER_ID = 1
ADDRESS1_lat = 1
ADDRESS1_lon = 1
ADDRESS2_lat = 2
ADDRESS2_lon = 2
ORDER_ID = 1


@pytest.fixture
async def drop_tables(test_client):
    await test_client.post(
        url="/driver/delete_all_drives",
    )
    await test_client.post(
        url="/passenger/delete_all_orders",
    )


async def add_new_passenger_drive_order(
    test_client: TestClient,
    email=EMAIL,
    start_lat=ADDRESS1_lat,
    start_lon=ADDRESS1_lon,
    destination_lat=ADDRESS1_lon,
    destination_lon=ADDRESS2_lon,
):
    parameter = DriveOrderRequestParam(
        currentUserEmail=email,
        startLat=start_lat,
        startLon=start_lon,
        destinationLat=destination_lat,
        destinationLon=destination_lon,
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )


async def test_post_request_drive(test_client: TestClient, drop_tables):
    # test for happy flow
    await add_new_passenger_drive_order(test_client, start_lat=1, start_lon=1, destination_lat=2, destination_lon=2)
    await add_new_passenger_drive_order(test_client, start_lat=3, start_lon=3, destination_lat=5, destination_lon=5)

    request_drive_request = DriverRequestDrive(
        email=EMAIL,
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )


async def test_post_request_drive_with_no_passenger_orders(test_client: TestClient, drop_tables):
    request_drive_request = DriverRequestDrive(
        email=EMAIL,
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert not resp.solutions


async def test_accept_drive(test_client: TestClient):
    request_drive_request = DriverRequestDrive(
        email=EMAIL,
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
    )
    assert resp.status_code == 200
