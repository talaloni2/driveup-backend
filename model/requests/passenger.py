from model.base_dto import BaseModel


class PassengerDriveOrderRequest(BaseModel):
    user_id: int
    passengers_amount: int
    source_location: str
    dest_location: str


class PassengerGetDrive(BaseModel):
    user_id: int
    order_id: int
