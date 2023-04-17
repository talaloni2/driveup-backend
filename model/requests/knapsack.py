from model.base_dto import BaseModel


class KnapsackItem(BaseModel):
    id: str
    volume: int
    value: int


class KnapsackSolverRequest(BaseModel):
    items: list[KnapsackItem]
    volume: int
    knapsack_id: str


class AcceptSolutionRequest(BaseModel):
    solution_id: str
    knapsack_id: str


class RejectSolutionsRequest(BaseModel):
    knapsack_id: str
