from model.base_dto import BaseModel


class DriverRequestDrive(BaseModel):
    email: str
    current_lat: float
    current_lon: float


class DriverAcceptDrive(BaseModel):
    email: str
    order_id: int


class DriverRejectDrive(BaseModel):
    email: str
