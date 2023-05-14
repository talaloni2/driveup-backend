from typing import Optional

from model.base_dto import BaseModel


class UserHandlerLoginRequest(BaseModel):
    username: str
    password: str


class UserHandlerCreateUserRequest(BaseModel):
    email: str
    password: str
    phone_number: str
    full_name: str
    car_model: Optional[str] = None
    car_color: Optional[str] = None
    plate_number: Optional[str] = None


class UserHandlerUpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    car_model: Optional[str] = None
    car_color: Optional[str] = None
    plate_number: Optional[str] = None
