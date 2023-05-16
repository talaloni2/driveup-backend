from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')


class UserSubscriptionMapSchema(BaseModel):
    subscription_name: Optional[str] = None
    user_email: Optional[str] = None
    card_owner_id: Optional[str] = None
    card_number: Optional[str] = None
    cvv: Optional[str] = None
    start_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class Request(GenericModel, Generic[T]):
    parameter: Optional[T] = Field(...)


class RequestUserSubscriptionMap(BaseModel):
    parameter: UserSubscriptionMapSchema = Field(...)


class Response(GenericModel, Generic[T]):
    code: int
    status: str
    message: str
    result: Optional[T]
