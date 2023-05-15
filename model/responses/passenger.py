from typing import Optional

from model.base_dto import BaseModel


class DriveOrderResponse(BaseModel):
    order_id: Optional[int] = None


class GetDriveResponse(BaseModel):
    drive_id: Optional[int] = None
