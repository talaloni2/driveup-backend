from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')


class LoginSchema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserSchema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    car_model: Optional[str] = None
    car_color: Optional[str] = None
    plate_number: Optional[str] = None

    class Config:
        orm_mode = True


class Request(GenericModel, Generic[T]):
    parameter: Optional[T] = Field(...)


class RequestLogin(BaseModel):
    parameter: LoginSchema = Field(...)


class RequestUser(BaseModel):
    parameter: UserSchema = Field(...)


class Response(GenericModel, Generic[T]):
    code: int
    status: str
    message: str
    result: Optional[T]
