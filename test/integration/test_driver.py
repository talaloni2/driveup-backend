from http import HTTPStatus

import pytest

from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, DriverRejectDrive
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.knapsack import SuggestedSolution
from model.responses.passenger import DriveOrderResponse
from model.responses.passenger import GetDriveResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
CURRENT_LAT = 1
CURRENT_LON = 1
ADDRESS1_lat = 1
ADDRESS1_lon = 1
ADDRESS2_lat = 2
ADDRESS2_lon = 2


@pytest.fixture
async def clear_tables(test_client):
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


async def test_post_request_drive(test_client: TestClient, clear_tables):
    # test for happy flow
    await add_new_passenger_drive_order(test_client, start_lat=1, start_lon=1, destination_lat=2, destination_lon=2)
    await add_new_passenger_drive_order(test_client, start_lat=3, start_lon=3, destination_lat=5, destination_lon=5)

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )


async def test_post_request_drive_with_no_passenger_orders(test_client: TestClient, clear_tables):
    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
        limits={},
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )


async def test_accept_drive(test_client: TestClient, clear_tables):
    # test happy flow
    """
    1) send passenger add order request
    2) send driver order drive request
    3) send accept drive for one of the seggested drives
    4) assert ok
    """
    random_order_id = None
    await add_new_passenger_drive_order(test_client, start_lat=1, start_lon=1, destination_lat=2, destination_lon=2)

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    for _id, solution in resp.solutions.items():
        if solution.items:
            random_order_id = _id
            break

    accept_drive_request = DriverAcceptDrive(order_id=random_order_id)

    await test_client.post(url="/driver/accept-drive", req_body=accept_drive_request, assert_status=HTTPStatus.OK)


async def test_accept_drive_non_existing_order_id(test_client: TestClient, clear_tables):
    await add_new_passenger_drive_order(test_client, start_lat=1, start_lon=1, destination_lat=2, destination_lon=2)

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
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


async def test_reject_drive(test_client: TestClient, clear_tables):
    # test happy flow
    """
    1) send passenger add order request
    2) send driver order drive request
    3) send reject drives
    4) assert ok
    """
    await add_new_passenger_drive_order(test_client, start_lat=1, start_lon=1, destination_lat=2, destination_lon=2)

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    reject_drive_request = DriverRejectDrive(email=EMAIL)

    await test_client.post(url="/driver/reject-drives", req_body=reject_drive_request, assert_status=HTTPStatus.OK)


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


async def test_accept_drive_passenger_order_updated(test_client):
    parameter = DriveOrderRequestParam(
        currentUserEmail=get_random_email(),
        startLat=2,
        startLon=2,
        destinationLat=3,
        destinationLon=3,
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    order_drive_resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )

    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
        limits={},
    )
    drive_offers = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    passenger_order_without_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}",
        resp_model=GetDriveResponse
    )

    assert len(drive_offers.solutions) > 0, "Solutions must not be empty"
    accepted_drive_id = next(iter(drive_offers.solutions.keys()))
    await test_client.post(
        url="/driver/accept-drive",
        req_body=DriverAcceptDrive(order_id=accepted_drive_id),
    )

    passenger_order_with_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}",
        resp_model=GetDriveResponse
    )

    assert passenger_order_without_drive.drive_id is None
    assert passenger_order_with_drive.drive_id is not None
