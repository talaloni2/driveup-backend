from datetime import datetime
from typing import Optional, Union

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class UserHandlerResponse(BaseModel):
    code: Optional[int]
    status: Optional[str]
    message: Optional[str]
    result: Optional[Union[dict, list]]
    detail: Optional[str]


class UserDetails(BaseModel):
    email: str
    full_name: str
    phone_number: str
    car_color: Optional[str]
    car_model: Optional[str]
    plate_number: Optional[str]


class UserHandlerGetByEmailResponse(UserHandlerResponse):
    result: Optional[UserDetails]


class GetUserByEmailResult(UserDetails):
    image_url: Optional[str]


class GetUserByEmailResponse(UserHandlerResponse):
    result: GetUserByEmailResult
