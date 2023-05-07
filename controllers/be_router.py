import http
import json

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from controllers import passenger
from model.requests.passenger import PassengerDriveOrderRequest, PassengerGetDrive

router = APIRouter()


@router.post("/passenger-order-drive")
async def handle_passenger_new_order(
    request: PassengerDriveOrderRequest,
):
    await passenger.add_drive_order(request)
    return JSONResponse(status_code=http.HTTPStatus.OK, content={}
    )


@router.post("/passenger-get-drive")
async def route_new_request(
    request: PassengerGetDrive,
):
    drive_id = await passenger.get_drive_by_order_id(request)
    return JSONResponse(
        status_code=http.HTTPStatus.OK,
        content={"drive_id": drive_id},
    )
