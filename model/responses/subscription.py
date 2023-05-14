from datetime import datetime
from typing import Optional, Union

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class SubscriptionHandlerResponse(BaseModel):
    code: Optional[int]
    status: Optional[str]
    message: Optional[str]
    result: Optional[Union[list, dict]]
    detail: Optional[str]
