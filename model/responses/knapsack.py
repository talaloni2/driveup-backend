from datetime import datetime

from model.base_dto import BaseModel
from model.requests.knapsack import KnapsackItem
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class SuggestedSolution(BaseModel):
    time: datetime
    solutions: dict[str, list[KnapsackItem]]


class AcceptSolutionResponse(BaseModel):
    result: AcceptResult


class RejectSolutionResponse(BaseModel):
    result: RejectResult
