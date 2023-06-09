from pydantic import BaseModel, Field


class DriveOrderRequestParam(BaseModel):
    startLat: float
    startLon: float
    destinationLat: float
    destinationLon: float
    numberOfPassengers: int


class PassengerDriveOrderRequest(BaseModel):
    parameter: DriveOrderRequestParam = Field(...)
