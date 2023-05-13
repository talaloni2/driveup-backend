from sqlalchemy import Column, Integer, Float, String, Enum, ARRAY
from enum import Enum


from model.base_db import Base

DRIVE_ORDER_TABLE = "drive_orders"

class DriveOrder(Base):
    __tablename__ = DRIVE_ORDER_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    passengers_amount = Column(Integer)
    status = Column(String, default='NEW')  # TODO convert to ENUM
    source_location = Column(ARRAY(Float, dimensions=2))
    dest_location = Column(ARRAY(Float, dimensions=2))
