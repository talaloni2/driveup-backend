from fastapi import APIRouter, Depends
import http


from component_factory import get_passenger_service

from model.requests.passenger import PassengerDriveOrderRequest, PassengerGetDrive
from model.drive_order import DriveOrder
from model.responses.passenger import DriveOrderResponse, GetDriveResponse
from service.passenger_service import PassengerService
from fastapi.responses import JSONResponse


router = APIRouter()


def _to_drive_order_response(order: DriveOrder):
    return DriveOrderResponse(order_id=order.id)


def _to_get_drive_response(drive_id: int):
    return GetDriveResponse(drive_id=drive_id)

@router.post("/order-drive")
async def handle_add_drive_order_request(
    order_request: PassengerDriveOrderRequest,  passenger_service: PassengerService = Depends(get_passenger_service)
) -> DriveOrderResponse:

    drive_order_response = await add_drive_order(order_request, passenger_service)
    return drive_order_response


async def add_drive_order(order_request: PassengerDriveOrderRequest, passenger_service: PassengerService):
        db_drive_order = DriveOrder(email=order_request.email, passengers_amount=order_request.passengers_amount,
                                    source_location=[order_request.source_location.lat, order_request.source_location.lon],
                                    dest_location=[order_request.dest_location.lat, order_request.dest_location.lon])

        order = await passenger_service.save(db_drive_order)
        return _to_drive_order_response(order)


@router.post("/get-drive")
async def handle_get_drive_request(
    request: PassengerGetDrive, passenger_service: PassengerService = Depends(get_passenger_service)
):
    drive_id = await get_drive_by_order_id(request, passenger_service)
    return JSONResponse(
        status_code=http.HTTPStatus.OK,
        content={"drive_id": drive_id},
    )


async def get_drive_by_order_id(
    request: PassengerGetDrive, passenger_service: PassengerService
) -> DriveOrderResponse:
    # drive_id = await get_drive_by_order_id(request)

    order = await passenger_service.get_by_order_id(request.order_id)
    return _to_drive_order_response(order)

