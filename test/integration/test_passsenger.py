from http import HTTPStatus

from model.requests.driver import DriverRequestDrive
from model.requests.passenger import PassengerDriveOrderRequest, DriveOrderRequestParam
from model.responses.knapsack import SuggestedSolution
from model.responses.passenger import DriveOrderResponse, GetDriveResponse, OrderHistoryNode
from model.responses.success import SuccessResponse
from test.utils.test_client import TestClient
from test.utils.utils import random_latitude, random_longitude

PASSENGER_AMOUNT = 1


async def test_post_add_drive_order(test_client: TestClient):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    assert resp.order_id > 0
    assert resp.estimated_cost > 0


async def test_get_drive(test_client: TestClient):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    await test_client.get(
        url=f"/passenger/get-drive/{resp.order_id}",
        resp_model=GetDriveResponse,
    )


async def test_cancel_drive(test_client: TestClient):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    await test_client.get(
        url=f"/passenger/get-drive/{resp.order_id}",
        resp_model=GetDriveResponse,
    )

    cancel_result = await test_client.delete(
        url=f"/passenger/cancel-order/{resp.order_id}",
        resp_model=SuccessResponse,
    )
    assert cancel_result.success

    await test_client.get(url=f"/passenger/get-drive/{resp.order_id}", assert_status=HTTPStatus.NOT_FOUND)


async def test_cancel_drive_fail(test_client: TestClient, clear_orders_tables: None):
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    resp = await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
    await test_client.get(
        url=f"/passenger/get-drive/{resp.order_id}",
        resp_model=GetDriveResponse,
    )

    request_drive_request = DriverRequestDrive(
        current_lat=random_latitude(parameter.startLat, 0.00001),
        current_lon=random_longitude(parameter.startLon, 0.00001),
    )

    await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
        resp_model=SuggestedSolution,
    )

    cancel_result = await test_client.delete(
        url=f"/passenger/cancel-order/{resp.order_id}",
        resp_model=SuccessResponse,
    )
    assert not cancel_result.success

    await test_client.get(
        url=f"/passenger/get-drive/{resp.order_id}",
        resp_model=GetDriveResponse,
    )


async def test_get_non_existing_drive(test_client: TestClient):
    await test_client.get(
        url=f"/passenger/get-drive/{pow(2, 30)}",
        assert_status=HTTPStatus.NOT_FOUND,
    )


async def test_order_history(test_client: TestClient, clear_orders_tables: None):
    await _order_drive(test_client)
    await _order_drive(test_client)

    response = [OrderHistoryNode(**a) for a in (await test_client.get(
        url=f"/passenger/order-history",
    )).json()]

    assert len(response) == 2


async def _order_drive(test_client) -> DriveOrderResponse:
    parameter = DriveOrderRequestParam(
        startLat=random_latitude(),
        startLon=random_longitude(),
        destinationLat=random_latitude(),
        destinationLon=random_longitude(),
        numberOfPassengers=1,
    )
    order_new_drive_request = PassengerDriveOrderRequest(parameter=parameter)
    return await test_client.post(
        url="/passenger/order-drive",
        req_body=order_new_drive_request,
        resp_model=DriveOrderResponse,
    )
