from datetime import datetime

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class KnapsackSolution(BaseModel):
    algorithm: str
    items: list[KnapsackItem]
    total_value: int


class SuggestedSolution(BaseModel):
    time: datetime
    solutions: dict[str, KnapsackSolution]


class AcceptSolutionResponse(BaseModel):
    result: AcceptResult


class RejectSolutionResponse(BaseModel):
    result: RejectResult


class ItemClaimedResponse(BaseModel):
    is_claimed: bool
