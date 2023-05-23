from sqlalchemy import Column, Integer, Float, String, Enum, ARRAY
from enum import Enum


from model.base_db import Base

DRIVE_ORDER_TABLE = "drive_orders"


class DriveOrderStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class DriveOrder(Base):
    __tablename__ = DRIVE_ORDER_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    passengers_amount = Column(Integer)
    status = Column(String, default='NEW')  # TODO convert to ENUM
    source_location = Column(ARRAY(Float, dimensions=1))
    dest_location = Column(ARRAY(Float, dimensions=1))
    drive_id = Column(Integer, default=None)
    frozen_by = Column(String) # driver's email


