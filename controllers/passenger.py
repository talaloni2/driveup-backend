from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from component_factory import (
    get_passenger_service,
    get_cost_estimation_service,
    get_directions_service,
    get_time_service,
)
from model.passenger_drive_order import PassengerDriveOrder
from model.requests.passenger import PassengerDriveOrderRequest
from model.responses.directions_api import DirectionsApiResponse
from model.responses.geocode import Geocode
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from service.cost_estimation_service import CostEstimationService
from service.currency_conversion_service import nis_to_usd
from service.directions_service import DirectionsService
from service.passenger_service import PassengerService
from service.time_service import TimeService

router = APIRouter()


def _to_drive_order_response(order: PassengerDriveOrder):
    return DriveOrderResponse(order_id=order.id, estimated_cost=order.estimated_cost)


def _to_get_drive_response(order: PassengerDriveOrder):
    return GetDriveResponse(
        drive_id=order.drive_id,
        origin=Geocode(latitude=order.source_location[0], longitude=order.source_location[1]),
        destination=Geocode(latitude=order.dest_location[0], longitude=order.dest_location[1]),
        estimated_cost=order.estimated_cost,
    )


@router.post("/order-drive")
async def handle_add_drive_order_request(
    order_request: PassengerDriveOrderRequest,
    passenger_service: PassengerService = Depends(get_passenger_service),
    cost_estimation_service: CostEstimationService = Depends(get_cost_estimation_service),
    time_service: TimeService = Depends(get_time_service),
    directions_service: DirectionsService = Depends(get_directions_service),
) -> DriveOrderResponse:
    cost_estimation = await _estimate_cost(cost_estimation_service, directions_service, order_request, time_service)

    drive_order = await add_drive_order(order_request, passenger_service, cost_estimation)
    return _to_drive_order_response(drive_order)


async def _estimate_cost(cost_estimation_service, directions_service, order_request, time_service):
    directions: DirectionsApiResponse = await directions_service.get_directions(
        Geocode(latitude=order_request.parameter.startLat, longitude=order_request.parameter.startLon),
        Geocode(latitude=order_request.parameter.destinationLat, longitude=order_request.parameter.destinationLon),
    )
    cost_estimation = nis_to_usd(cost_estimation_service.estimate_cost(time_service.now(), directions))
    return cost_estimation


async def add_drive_order(
    order_request: PassengerDriveOrderRequest, passenger_service: PassengerService, cost_estimation: float
) -> PassengerDriveOrder:
    db_drive_order = PassengerDriveOrder(
        email=order_request.parameter.currentUserEmail,
        passengers_amount=order_request.parameter.numberOfPassengers,
        source_location=[order_request.parameter.startLat, order_request.parameter.startLon],
        dest_location=[order_request.parameter.destinationLat, order_request.parameter.destinationLon],
        estimated_cost=cost_estimation,
    )

    order = await passenger_service.save(db_drive_order)
    return order


@router.get("/get-drive/{orderId}")
async def handle_get_drive_request(orderId: int, passenger_service: PassengerService = Depends(get_passenger_service)):
    drive_order_response = await passenger_service.get_by_order_id(orderId)
    if not drive_order_response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"message": "Could not find passenger order"})

    return _to_get_drive_response(drive_order_response)


@router.post("/delete_all_orders")
async def delete_drives(
        passenger_service: PassengerService = Depends(get_passenger_service)
):
    await passenger_service.drop_table_passenger_drive_order()

