from datetime import datetime
from typing import Optional

from model.base_dto import BaseModel

from model.requests.knapsack import KnapsackItem


class DriverSuggestedDrives(BaseModel):
    driver_id: int
    suggested_drives: list[KnapsackItem]


class Geocode(BaseModel):
    latitude: float
    longitude: float


class OrderLocation(BaseModel):
    user_email: str
    is_driver: bool
    is_start_address: bool
    address: Geocode
    price: int


class DriveDetails(BaseModel):
    time: datetime
    id: str
    order_locations: list[OrderLocation]
    total_price: int

#
# class DriverGetDriveResponse(BaseModel):
#     drive_id: int