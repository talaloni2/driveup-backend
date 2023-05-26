from datetime import datetime

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.responses.geocode import Geocode


class DriverSuggestedDrives(BaseModel):
    driver_id: int
    suggested_drives: list[KnapsackItem]


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
