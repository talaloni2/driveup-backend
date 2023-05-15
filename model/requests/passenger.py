from model.base_dto import BaseModel

class Address(BaseModel):
    lon: int
    lat: int

class PassengerDriveOrderRequest(BaseModel):
    email: str
    passengers_amount: int
    source_lat: float
    source_lon: float
    dest_lat: float
    dest_lon: float
    passengers_amount: int


class PassengerGetDrive(BaseModel):
    email: str
    order_id: int
