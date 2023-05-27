from functools import partial
from typing import Optional, Any

from model.base_dto import BaseModel
from enum import Enum


class LimitValues(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None


class Limit(Enum):
    pick_up_distance = "pick_up_distance"
    ride_distance = "ride_distance"


class DriverRequestDrive(BaseModel):
    current_lat: float
    current_lon: float
    limits: dict[Limit, LimitValues] = {}


class DriverAcceptDrive(BaseModel):
    order_id: str


class DriverRejectDrive(BaseModel):
    email: str
