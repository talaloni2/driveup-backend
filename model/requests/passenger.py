from model.base_dto import BaseModel

class Address(BaseModel):
    lon: int
    lat: int

class PassengerDriveOrderRequest(BaseModel):
    user_id: int
    passengers_amount: int
    source_location: Address
    dest_location: Address


class PassengerGetDrive(BaseModel):
    user_id: int
    order_id: int
