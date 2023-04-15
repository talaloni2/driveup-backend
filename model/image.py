from sqlalchemy import Column, Integer, LargeBinary, String

from model.base_db import Base


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    image_data = Column(LargeBinary)
    filename = Column(String)
