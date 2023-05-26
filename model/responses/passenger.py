from typing import Optional

from model.base_dto import BaseModel
from model.responses.geocode import Geocode


class DriveOrderResponse(BaseModel):
    order_id: Optional[int] = None
    estimated_cost: float = 0


class GetDriveResponse(BaseModel):
    drive_id: Optional[str] = None
    origin: Geocode
    destination: Geocode
    estimated_cost: float = 0
