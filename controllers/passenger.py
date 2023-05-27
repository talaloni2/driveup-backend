from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from component_factory import (
    get_passenger_service,
    get_cost_estimation_service,
    get_directions_service,
    get_time_service,
)
from controllers.utils import AuthenticatedUser, authenticated_user, adjust_timezone
from model.passenger_drive_order import PassengerDriveOrder, PassengerDriveOrderStatus
from model.requests.passenger import PassengerDriveOrderRequest
from model.responses.directions_api import DirectionsApiResponse
from model.responses.geocode import Geocode
from model.responses.passenger import DriveOrderResponse, GetDriveResponse, OrderHistoryNode
from model.responses.success import SuccessResponse
from service.cost_estimation_service import CostEstimationService
from service.currency_conversion_service import nis_to_usd
from service.directions_service import DirectionsService
from service.passenger_service import PassengerService
from service.time_service import TimeService

router = APIRouter()


def _to_drive_order_response(order: PassengerDriveOrder, time_service: TimeService):
    return DriveOrderResponse(order_id=order.id, estimated_cost=order.estimated_cost, time=adjust_timezone(order.time, time_service))


def _to_get_drive_response(order: PassengerDriveOrder, time_service: TimeService):
    return GetDriveResponse(
        drive_id=order.drive_id,
        origin=Geocode(latitude=order.source_location[0], longitude=order.source_location[1]),
        destination=Geocode(latitude=order.dest_location[0], longitude=order.dest_location[1]),
        estimated_cost=order.estimated_cost,
        time=adjust_timezone(order.time, time_service)
    )


@router.post("/order-drive")
async def handle_add_drive_order_request(
    order_request: PassengerDriveOrderRequest,
    passenger_service: PassengerService = Depends(get_passenger_service),
    cost_estimation_service: CostEstimationService = Depends(get_cost_estimation_service),
    time_service: TimeService = Depends(get_time_service),
    directions_service: DirectionsService = Depends(get_directions_service),
    user: AuthenticatedUser = Depends(authenticated_user),
) -> DriveOrderResponse:
    cost_estimation = await _estimate_cost(cost_estimation_service, directions_service, order_request, time_service)

    drive_order = await add_drive_order(user.email, order_request, passenger_service, cost_estimation, time_service.utcnow())
    return _to_drive_order_response(drive_order, time_service)


async def _estimate_cost(cost_estimation_service, directions_service, order_request, time_service):
    directions: DirectionsApiResponse = await directions_service.get_directions(
        Geocode(latitude=order_request.parameter.startLat, longitude=order_request.parameter.startLon),
        Geocode(latitude=order_request.parameter.destinationLat, longitude=order_request.parameter.destinationLon),
    )
    cost_estimation = nis_to_usd(cost_estimation_service.estimate_cost(time_service.now(), directions))
    return cost_estimation


async def add_drive_order(
    user_id: str, order_request: PassengerDriveOrderRequest, passenger_service: PassengerService, cost_estimation: float,
    time: datetime
) -> PassengerDriveOrder:
    db_drive_order = PassengerDriveOrder(
        email=user_id,
        passengers_amount=order_request.parameter.numberOfPassengers,
        source_location=[order_request.parameter.startLat, order_request.parameter.startLon],
        dest_location=[order_request.parameter.destinationLat, order_request.parameter.destinationLon],
        estimated_cost=cost_estimation,
        time=time
    )

    order = await passenger_service.save(db_drive_order)
    return order


@router.get("/get-drive/{order_id}")
async def handle_get_drive_request(
    order_id: int,
    user: AuthenticatedUser = Depends(authenticated_user),
    passenger_service: PassengerService = Depends(get_passenger_service),
    time_service: TimeService = Depends(get_time_service),
) -> GetDriveResponse:
    drive_order_response = await passenger_service.get_by_order_and_user_id(user.email, order_id)
    if not drive_order_response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"message": "Could not find passenger order"})

    return _to_get_drive_response(drive_order_response, time_service)


@router.delete("/cancel-order/{order_id}")
async def cancel_order(
    order_id: int,
    user: AuthenticatedUser = Depends(authenticated_user),
    passenger_service: PassengerService = Depends(get_passenger_service),
) -> SuccessResponse:
    is_cancelled = await passenger_service.cancel_order(user.email, order_id)
    return SuccessResponse(success=is_cancelled)


def _to_order_history_node(order_details: PassengerDriveOrder, time_service: TimeService) -> OrderHistoryNode:
    return OrderHistoryNode(
        driver_id=order_details.frozen_by if order_details.status != PassengerDriveOrderStatus.FROZEN else None,
        order_id=order_details.id,
        time=adjust_timezone(order_details.time, time_service),
        cost=order_details.estimated_cost,
        drive_id=order_details.drive_id,
    )


@router.get("/order-history/")
async def order_history(
    page: int = 1,
    size: int = 20,
    user: AuthenticatedUser = Depends(authenticated_user),
    time_service: TimeService = Depends(get_time_service),
    passenger_service: PassengerService = Depends(get_passenger_service),
) -> list[OrderHistoryNode]:
    page = max(page - 1, 0)
    drive_order_response = await passenger_service.get_by_user_email(user.email, page, size)
    if not drive_order_response:
        return []

    return [_to_order_history_node(o, time_service) for o in drive_order_response]
