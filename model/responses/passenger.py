from datetime import datetime
from typing import Optional

from model.base_dto import BaseModel
from model.responses.geocode import Geocode


class DriveOrderResponse(BaseModel):
    order_id: Optional[int] = None
    estimated_cost: float = 0
    time: datetime


class GetDriveResponse(BaseModel):
    drive_id: Optional[str] = None
    origin: Geocode
    destination: Geocode
    estimated_cost: float = 0
    time: datetime
    estimated_driver_arrival: Optional[datetime] = None


class OrderHistoryNode(BaseModel):
    driver_id: Optional[str] = None
    order_id: int
    time: datetime
    cost: float
    drive_id: Optional[str]

