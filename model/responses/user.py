from datetime import datetime
from typing import Optional

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class UserHandlerResponse(BaseModel):
    code: int
    status: str
    message: str
    result: Optional[dict]
