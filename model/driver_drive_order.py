from sqlalchemy import Column, Integer, Float, String, Enum, ARRAY, DateTime, JSON
from enum import Enum


from model.base_db import Base

DRIVER_DRIVE_ORDER_TABLE = "driver_drive_orders"


class DriveOrderStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class DriverDriveOrder(Base):
    __tablename__ = DRIVER_DRIVE_ORDER_TABLE
    id = Column(String, primary_key=True)
    time = Column(DateTime)
    driver_id = Column(String)
    expires_at = Column(DateTime)
    passengers_amount = Column(Integer)
    passenger_orders = Column(ARRAY(JSON))
    status = Column(String)
    algorithm = Column(String)
