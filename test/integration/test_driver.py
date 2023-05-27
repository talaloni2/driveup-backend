import time
from http import HTTPStatus

import pytest

from component_factory import (
    get_passenger_service,
    create_db_engine,
    get_database_url,
    get_config,
    get_db_session_maker,
    get_driver_service,
)
from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, DriverRejectDrive
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.geocode import Geocode
from model.responses.knapsack import SuggestedSolution
from model.responses.passenger import DriveOrderResponse
from model.responses.passenger import GetDriveResponse
from service.driver_service import DriverService
from service.passenger_service import PassengerService
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email, random_latitude, random_longitude

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1


async def add_new_passenger_drive_order(
    test_client: TestClient,
    source: Geocode = None,
    dest: Geocode = None
) -> DriveOrderResponse:
    source = source or Geocode(latitude=random_latitude(), longitude=random_longitude())
    dest = dest or Geocode(latitude=random_latitude(), longitude=random_longitude())
    parameter = DriveOrderRequestParam(
        startLat=source.latitude,
        startLon=source.longitude,
        destinationLat=dest.latitude,
        destinationLon=dest.longitude,
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    return await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )


@pytest.mark.asyncio
async def test_post_request_drive(test_client: TestClient, clear_orders_tables):
    # test for happy flow
    await add_new_passenger_drive_order(test_client)
    await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )


@pytest.mark.asyncio
async def test_post_request_drive_with_no_passenger_orders(test_client: TestClient, clear_orders_tables):
    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
        limits={},
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )


@pytest.mark.asyncio
async def test_accept_drive(test_client: TestClient, clear_orders_tables):
    # test happy flow
    """
    1) send passenger add order request
    2) send driver order drive request
    3) send accept drive for one of the seggested drives
    4) assert ok
    """
    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )

    await add_new_passenger_drive_order(test_client, Geocode(latitude=request_drive_request.current_lat, longitude=request_drive_request.current_lon))

    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    random_order_id = None
    for _id, solution in resp.solutions.items():
        if solution.items:
            random_order_id = _id
            break

    accept_drive_request = DriverAcceptDrive(order_id=random_order_id)

    await test_client.post(url="/driver/accept-drive", req_body=accept_drive_request, assert_status=HTTPStatus.OK)


@pytest.mark.asyncio
async def test_accept_drive_non_existing_order_id(test_client: TestClient, clear_orders_tables):
    await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )

    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    accept_drive_request = DriverAcceptDrive(order_id="not_existing_order_id")

    await test_client.post(
        url="/driver/accept-drive", req_body=accept_drive_request, assert_status=HTTPStatus.NOT_ACCEPTABLE
    )


@pytest.mark.asyncio
async def test_reject_drive(test_client: TestClient, clear_orders_tables):
    # test happy flow
    """
    1) send passenger add order request
    2) send driver order drive request
    3) send reject drives
    4) assert ok
    """
    await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    reject_drive_request = DriverRejectDrive(email=EMAIL)

    await test_client.post(url="/driver/reject-drives", req_body=reject_drive_request, assert_status=HTTPStatus.OK)


@pytest.mark.asyncio
async def test_request_drives_suggestion_already_exists(test_client):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
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


@pytest.mark.asyncio
async def test_accept_drive_passenger_order_updated(test_client):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    order_drive_resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
        limits={},
    )
    drive_offers = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    passenger_order_without_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse
    )

    assert len(drive_offers.solutions) > 0, "Solutions must not be empty"
    accepted_drive_id = next(iter(drive_offers.solutions.keys()))
    await test_client.post(
        url="/driver/accept-drive",
        req_body=DriverAcceptDrive(order_id=accepted_drive_id),
    )

    time.sleep(0.3)
    passenger_order_with_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse
    )

    assert passenger_order_without_drive.drive_id is None
    assert passenger_order_with_drive.drive_id is not None
