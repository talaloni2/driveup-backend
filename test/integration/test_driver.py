import datetime
import time
from datetime import timedelta
from http import HTTPStatus
from typing import NamedTuple, Optional
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytz
from _pytest.outcomes import fail
from pytest_mock import MockerFixture

from component_factory import (
    get_knapsack_service, get_passenger_service, get_database_url, get_db_session_maker, create_db_engine, get_config,
    get_time_service,
)
from controllers import driver
from controllers.utils import authenticated_user
from model.passenger_drive_order import PassengerDriveOrderStatus
from model.requests.driver import DriverRequestDrive, DriverAcceptDrive
from model.requests.knapsack import KnapsackItem
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.driver import DriveDetails, OrderLocation
from model.responses.geocode import Geocode
from model.responses.knapsack import SuggestedSolution, KnapsackSolution
from model.responses.passenger import DriveOrderResponse
from model.responses.passenger import GetDriveResponse
from model.responses.success import SuccessResponse
from model.responses.user import UserHandlerResponse
from model.user_schemas import RequestUser, UserSchema
from server import app
from service.knapsack_service import KnapsackService
from service.passenger_service import PassengerService
from service.time_service import TimeService
from test.utils.test_client import TestClient
from test.utils.utils import random_latitude, random_longitude, get_random_string, get_random_email

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1


class _AcceptedDrive(NamedTuple):
    drive_id: str
    order_ids: list[int]


@pytest.fixture
async def passenger_service(event_loop) -> PassengerService:
    async with get_db_session_maker(create_db_engine(get_database_url(get_config())))() as session:
        async with session.begin():
            yield get_passenger_service(session)


async def add_new_passenger_drive_order(
    test_client: TestClient,
    source: Geocode = None,
    dest: Geocode = None,
    user_token: Optional[str] = None
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
        headers={"Authorization": f"Bearer {user_token}"}
    )


async def test_post_request_drive(test_client: TestClient, clear_orders_tables):
    # test for happy flow
    await add_new_passenger_drive_order(test_client)
    await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert all(suggestion.total_value > 0 for suggestion in resp.solutions.values())


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


async def test_accept_drive(test_client: TestClient, clear_orders_tables):
    # test happy flow
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


async def test_reject_drive(test_client: TestClient, clear_orders_tables, passenger_service):

    passenger_order: DriveOrderResponse = await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert (await passenger_service.get_by_order_id(passenger_order.order_id)).status == PassengerDriveOrderStatus.FROZEN

    assert resp.solutions

    resp = await test_client.post(url="/driver/reject-drives", resp_model=SuccessResponse, assert_status=HTTPStatus.OK)
    assert resp.success
    assert (await passenger_service.get_by_order_id(passenger_order.order_id)).status == PassengerDriveOrderStatus.NEW


async def test_reject_drive_passenger_request_reclaimed(test_client: TestClient, clear_orders_tables, passenger_service):

    passenger_order: DriveOrderResponse = await add_new_passenger_drive_order(test_client)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert (await passenger_service.get_by_order_id(passenger_order.order_id)).status == PassengerDriveOrderStatus.FROZEN

    assert resp.solutions

    resp = await test_client.post(url="/driver/reject-drives", resp_model=SuccessResponse, assert_status=HTTPStatus.OK)
    assert resp.success
    assert (await passenger_service.get_by_order_id(passenger_order.order_id)).status == PassengerDriveOrderStatus.NEW

    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert (await passenger_service.get_by_order_id(
        passenger_order.order_id)).status == PassengerDriveOrderStatus.FROZEN


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


@pytest.fixture
def mock_time_service() -> TimeService:
    time_service: TimeService = MagicMock()
    time_service.utcnow = MagicMock(return_value=datetime.datetime.utcnow())
    # noinspection PyPropertyAccess
    time_service.timezone = pytz.timezone("Asia/Jerusalem")
    time_service.now = MagicMock(return_value=datetime.datetime.now(time_service.timezone))
    app.dependency_overrides[get_time_service] = lambda: time_service
    yield time_service
    del app.dependency_overrides[get_time_service]


async def test_request_drives_suggestion_previous_drive_expired(test_client, mock_time_service, clear_orders_tables):

    await _add_passenger_drive_order([], test_client)

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

    mock_time_service.utcnow = MagicMock(return_value=datetime.datetime.utcnow() + timedelta(days=1))
    mock_time_service.now = MagicMock(return_value=datetime.datetime.now(mock_time_service.timezone) + timedelta(days=1))
    await _add_passenger_drive_order([], test_client)

    second_resp = await test_client.post(
        url="/driver/request-drives?force_reject=false",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    assert len(first_resp.solutions) > 0
    assert len(second_resp.solutions) > 0
    assert first_resp != second_resp


async def test_accept_drive_passenger_order_updated(test_client, unauthenticated):
    user_token = await _create_new_user_get_token(test_client, get_random_email())
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
        headers={"Authorization": f"Bearer {user_token}"}
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
        headers={"Authorization": f"Bearer {user_token}"}
    )

    passenger_order_without_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert len(drive_offers.solutions) > 0, "Solutions must not be empty"
    accepted_drive_id = next(iter(drive_offers.solutions.keys()))
    await test_client.post(
        url="/driver/accept-drive",
        req_body=DriverAcceptDrive(order_id=accepted_drive_id),
        headers={"Authorization": f"Bearer {user_token}"}
    )

    time.sleep(0.3)
    passenger_order_with_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert passenger_order_without_drive.drive_id is None
    assert passenger_order_with_drive.drive_id is not None


async def test_get_drive_details(test_client, clear_orders_tables, accept_drive: _AcceptedDrive):
    _id = accept_drive.drive_id
    await test_client.get(url=f"/driver/drive-details/{_id}", resp_model=DriveDetails,  assert_status=HTTPStatus.OK)


async def test_get_drive_details_preview(test_client, clear_orders_tables, request_drive: tuple[str, KnapsackSolution]):
    _id = request_drive[0]
    await test_client.get(url=f"/driver/drive-details-preview/{_id}", resp_model=DriveDetails,  assert_status=HTTPStatus.OK)


async def test_finish_drive_sanity(test_client, clear_orders_tables, accept_drive: _AcceptedDrive):
    _id = accept_drive.drive_id
    await test_client.post(url=f"/driver/finish-drive/{_id}", resp_model=SuccessResponse, assert_status=HTTPStatus.OK)

    passenger_orders = [
        await test_client.get(url=f"/passenger/get-drive/{order_id}", resp_model=GetDriveResponse)
        for order_id in accept_drive.order_ids
    ]

    assert all(order.status == PassengerDriveOrderStatus.FINISHED for order in passenger_orders)


async def test_finish_non_accepted_drive(test_client, request_drive: tuple[str, KnapsackSolution]):
    _id = request_drive[0]
    await test_client.post(url=f"/driver/finish-drive/{_id}", assert_status=HTTPStatus.BAD_REQUEST)


async def test_finish_assigned_to_another_drive(test_client, accept_drive: _AcceptedDrive):
    await _unauthenticate()
    new_driver = await _create_new_user(test_client, get_random_email())
    new_driver_token = new_driver.result["token"]
    _id = accept_drive.drive_id
    await test_client.post(url=f"/driver/finish-drive/{_id}", headers={"Authorization": f"Bearer {new_driver_token}"}, assert_status=HTTPStatus.BAD_REQUEST)


async def _unauthenticate():
    if authenticated_user in app.dependency_overrides:
        del app.dependency_overrides[authenticated_user]


@pytest.fixture
async def request_drive(test_client, clear_orders_tables) -> tuple[str, KnapsackSolution]:
    order_ids = []
    await _add_passenger_drive_order(order_ids, test_client)
    await _add_passenger_drive_order(order_ids, test_client)
    await _add_passenger_drive_order(order_ids, test_client)

    resp: SuggestedSolution = await _request_drive(test_client)

    return _get_first_non_empty_order(resp)


@pytest.fixture
async def accept_drive(test_client, request_drive) -> _AcceptedDrive:
    random_driver_order_id, random_driver_order = request_drive
    await _perform_accept_drive(random_driver_order_id, test_client)
    return _AcceptedDrive(drive_id=random_driver_order_id, order_ids=[int(i.id) for i in random_driver_order.items])


async def _perform_accept_drive(random_driver_order_id, test_client):
    accept_drive_request = DriverAcceptDrive(order_id=random_driver_order_id)
    await test_client.post(url="/driver/accept-drive", req_body=accept_drive_request)


def _get_first_non_empty_order(resp) -> tuple[str, KnapsackSolution]:
    for _id, solution in resp.solutions.items():
        if solution.items:
            return _id, solution
    fail("There should have been a solution with items.")


async def _request_drive(test_client) -> SuggestedSolution:
    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )
    return resp


async def _add_passenger_drive_order(order_ids, test_client):
    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
    )
    ride_request = await add_new_passenger_drive_order(test_client, Geocode(latitude=request_drive_request.current_lat,
                                                                            longitude=request_drive_request.current_lon))
    order_ids.append(ride_request.order_id)


@pytest.fixture
def mock_knapsack_service() -> KnapsackService:
    service_mock = MagicMock()
    app.dependency_overrides[get_knapsack_service] = lambda: service_mock
    yield service_mock
    del app.dependency_overrides[get_knapsack_service]


async def _create_new_user(test_client: TestClient, new_username: str) -> UserHandlerResponse:
    return (
        await test_client.post(
            url="/users/",
            req_body=RequestUser(
                parameter=UserSchema(
                    email=new_username,
                    password="1234",
                    phone_number=new_username,
                    full_name=new_username,
                )
            ),
            resp_model=UserHandlerResponse,
        )
    )


async def _create_new_user_get_token(test_client: TestClient, new_username: str) -> str:
    return (
        await test_client.post(
            url="/users/",
            req_body=RequestUser(
                parameter=UserSchema(
                    email=new_username,
                    password="1234",
                    phone_number=new_username,
                    full_name=new_username,
                )
            ),
            resp_model=UserHandlerResponse,
        )
    ).result["token"]


async def test_accept_drive_passenger_estimated_time_updated(test_client, mock_knapsack_service, mocker: MockerFixture, unauthenticated):
    accepted_drive_id = get_random_string()
    time_service = TimeService()
    now = time_service.utcnow()
    mock_knapsack_service.accept_solution = AsyncMock(return_value=True)
    mock_knapsack_service.reject_solutions = AsyncMock(return_value=True)
    first_passenger_email = f"test_user_{get_random_string()}@gmail.com"
    first_passenger = await _create_new_user(test_client, first_passenger_email)
    first_passenger_token = first_passenger.result["token"]
    second_passenger_email = f"test_user_{get_random_string()}@gmail.com"
    second_passenger = await _create_new_user(test_client, second_passenger_email)
    second_passenger_token = second_passenger.result["token"]
    user_driver_email = f"test_user_{get_random_string()}@gmail.com"
    user_driver = await _create_new_user(test_client, user_driver_email)
    user_driver_token = user_driver.result["token"]
    first_passenger_order = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=first_passenger_order)
    order_drive_resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
        headers={"Authorization": f"Bearer {first_passenger_token}"}
    )

    second_passenger_order = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=second_passenger_order)
    second_drive_resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
        headers={"Authorization": f"Bearer {second_passenger_token}"}
    )

    mock_knapsack_service.suggest_solution = AsyncMock(return_value=SuggestedSolution(time=now, expires_at=now + timedelta(seconds=100), solutions={accepted_drive_id: KnapsackSolution(algorithm="mock", items=[KnapsackItem(id=str(order_drive_resp.order_id), value=1, volume=1), KnapsackItem(id=str(second_drive_resp.order_id), value=1, volume=1)])}))
    future = AsyncMock()
    future.return_value = (
        DriveDetails(
            time=time_service.now(),
            id=accepted_drive_id,
            order_locations=[
                OrderLocation(
                    user_email=user_driver_email,
                    is_driver=True,
                    is_start_address=True,
                    address=Geocode(latitude=32.080209, longitude=34.898453),
                    price=10,
                ),
                OrderLocation(
                    user_email=first_passenger_email,
                    is_driver=False,
                    is_start_address=True,
                    address=Geocode(latitude=first_passenger_order.startLat, longitude=first_passenger_order.startLon),
                    price=10,
                ),
                OrderLocation(
                    user_email=second_passenger_email,
                    is_driver=False,
                    is_start_address=True,
                    address=Geocode(latitude=second_passenger_order.startLat, longitude=second_passenger_order.startLon),
                    price=10,
                ),
                OrderLocation(
                    user_email=first_passenger_token,
                    is_driver=False,
                    is_start_address=False,
                    address=Geocode(latitude=first_passenger_order.destinationLat, longitude=first_passenger_order.destinationLon),
                    price=10,
                ),
                OrderLocation(
                    user_email=second_passenger_token,
                    is_driver=False,
                    is_start_address=False,
                    address=Geocode(latitude=second_passenger_order.destinationLat, longitude=second_passenger_order.destinationLon),
                    price=10,
                ),
            ],
            total_price=20,
        )
    )
    mocker.patch.object(driver, "order_details", side_effect=future)

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(),
        current_lon=random_longitude(),
        limits={},
    )
    drive_offers = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
        headers={"Authorization": f"Bearer {user_driver_token}"}
    )

    passenger_order_without_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse,
        headers={"Authorization": f"Bearer {first_passenger_token}"}
    )

    assert len(drive_offers.solutions) > 0, "Solutions must not be empty"
    await test_client.post(
        url="/driver/accept-drive",
        req_body=DriverAcceptDrive(order_id=accepted_drive_id),
        headers={"Authorization": f"Bearer {user_driver_token}"}
    )

    time.sleep(0.3)
    first_passenger_order_with_drive = await test_client.get(
        url=f"/passenger/get-drive/{order_drive_resp.order_id}", resp_model=GetDriveResponse,
        headers={"Authorization": f"Bearer {first_passenger_token}"}
    )
    second_passenger_order_with_drive = await test_client.get(
        url=f"/passenger/get-drive/{second_drive_resp.order_id}", resp_model=GetDriveResponse,
        headers={"Authorization": f"Bearer {second_passenger_token}"}
    )

    assert passenger_order_without_drive.drive_id is None
    assert first_passenger_order_with_drive.estimated_driver_arrival is not None
    assert first_passenger_order_with_drive.estimated_driver_arrival is not None
    assert second_passenger_order_with_drive.estimated_driver_arrival is not None
    assert first_passenger_order_with_drive.estimated_driver_arrival < second_passenger_order_with_drive.estimated_driver_arrival

