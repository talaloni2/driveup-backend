from fastapi import APIRouter, Depends
import http


from component_factory import get_passenger_service

from model.requests.passenger import PassengerDriveOrderRequest
from model.drive_order import DriveOrder
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from service.passenger_service import PassengerService
from fastapi.responses import JSONResponse


router = APIRouter()


def _to_drive_order_response(order: DriveOrder):
    return DriveOrderResponse(order_id=order.id)


def _to_get_drive_response(order: DriveOrder):
    if order:
        return GetDriveResponse(drive_id=order.drive_id)
    return GetDriveResponse(drive_id=None)

@router.post("/order-drive")
async def handle_add_drive_order_request(
    order_request: PassengerDriveOrderRequest,  passenger_service: PassengerService = Depends(get_passenger_service)
) -> DriveOrderResponse:

    drive_order_response = await add_drive_order(order_request, passenger_service)
    return drive_order_response


async def add_drive_order(order_request: PassengerDriveOrderRequest, passenger_service: PassengerService):
        db_drive_order = DriveOrder(email=order_request.parameter.currentUserEmail, passengers_amount=order_request.parameter.numberOfPassengers,
                                    source_location=[order_request.parameter.startLat, order_request.parameter.startLon],
                                    dest_location=[order_request.parameter.destinationLat, order_request.parameter.destinationLon])

        order = await passenger_service.save(db_drive_order)
        return _to_drive_order_response(order)


@router.get("/get-drive/{orderId}")
async def handle_get_drive_request(
    orderId: int, passenger_service: PassengerService = Depends(get_passenger_service)
):
    drive_order_response = await get_drive_by_order_id(orderId, passenger_service)
    return drive_order_response


async def get_drive_by_order_id(
    order_id, passenger_service: PassengerService
) -> GetDriveResponse:

    order = await passenger_service.get_by_order_id(order_id)
    return _to_get_drive_response(order)

