from sqlalchemy import Column, Integer, Float, String, Enum, ARRAY
from enum import Enum


from model.base_db import Base

DRIVE_ORDER_TABLE = "drive_orders"

class DriveOrder(Base):
    __tablename__ = DRIVE_ORDER_TABLE
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    passengers_amount = Column(Integer)
    status = Column(Enum('NEW', 'IN_PROGRESS', 'DONE'), default='NEW')
    source_location = Column(ARRAY(Float, dimensions=2))
    dest_location = Column(ARRAY(Float, dimensions=2))
