from typing import Optional

from model.base_dto import BaseModel
from enum import Enum


class Limit(Enum):
    pick_up_distance = "pick_up_distance"
    ride_distance = "ride_distance"


class LimitValues(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None


class DriverRequestDrive(BaseModel):
    email: str
    current_lat: float
    current_lon: float
    limits: dict[Limit, LimitValues] = {}


class DriverAcceptDrive(BaseModel):
    email: str
    order_id: int


class DriverRejectDrive(BaseModel):
    email: str
