from fastapi import APIRouter, Depends

from component_factory import get_passenger_service

from model.requests.passenger import PassengerDriveOrderRequest, PassengerGetDrive
from model.drive_order import DriveOrder
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from service.passenger_service import PassengerService

router = APIRouter()


def _to_drive_order_response(order: DriveOrder):
    return DriveOrderResponse(order_id=order.id)


def _to_get_drive_response(drive_id: int):
    return GetDriveResponse(drive_id=drive_id)


async def add_drive_order(
    order: PassengerDriveOrderRequest, passenger_service: PassengerService = Depends(get_passenger_service)
) -> DriveOrderResponse:
    db_drive_order = DriveOrder(user_id=order.user_id, passengers_amount=order.passengers_amount,
                                source_location=order.source_location,
                                dest_location=order.dest_location,
    )
    order = await passenger_service.save(db_drive_order)
    return _to_drive_order_response(order)


async def get_drive_by_order_id(
    order: PassengerGetDrive, passenger_service: PassengerService = Depends(get_passenger_service)
) -> DriveOrderResponse:
    order = await passenger_service.get_by_order_id(order.order_id)
    return _to_drive_order_response(order)

