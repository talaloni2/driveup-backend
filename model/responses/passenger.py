from model.base_dto import BaseModel


class DriveOrderResponse(BaseModel):
    order_id: int


class GetDriveResponse(BaseModel):
    drive_id: int
