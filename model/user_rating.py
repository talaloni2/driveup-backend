from sqlalchemy import Column, Integer, String, FLOAT

from model.base_db import Base

USERS_TABLE = "users"
USER_RATING_TABLE = "users_rating"


class UserRating(Base):
    __tablename__ = USER_RATING_TABLE
    email = Column(String, primary_key=True)
    rating = Column(FLOAT)
    raters_count = Column(Integer)
