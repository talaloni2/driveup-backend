from pydantic import BaseModel, Field

# class Address(BaseModel):
#     lon: int
#     lat: int
class DriveOrderRequestParam(BaseModel):
    currentUserEmail: str
    startLat: float
    startLon: float
    destinationLat: float
    destinationLon: float
    numberOfPassengers: int
class PassengerDriveOrderRequest(BaseModel):
    parameter: DriveOrderRequestParam = Field(...)



# class PassengerGetDrive(BaseModel):
#     email: str
#     order_id: int
