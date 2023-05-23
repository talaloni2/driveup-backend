from sqlalchemy import Column, Integer, Float, String, Enum, ARRAY
from enum import Enum


from model.base_db import Base

PASSENGER_DRIVE_ORDER_TABLE = "passenger_drive_orders"


class PassengerDriveOrderStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    FINISHED = "FINISHED"


class PassengerDriveOrder(Base):
    __tablename__ = PASSENGER_DRIVE_ORDER_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    passengers_amount = Column(Integer)
    status = Column(String, default=PassengerDriveOrderStatus.NEW)
    source_location = Column(ARRAY(Float, dimensions=1))
    dest_location = Column(ARRAY(Float, dimensions=1))
    drive_id = Column(Integer, default=None)
    frozen_by = Column(String) # driver's email


