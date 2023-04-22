import asyncio
from uuid import uuid4

from httpx import AsyncClient

from model.requests.knapsack import KnapsackItem, KnapsackSolverRequest, AcceptSolutionRequest, RejectSolutionsRequest
from model.responses.knapsack import SuggestedSolution, AcceptSolutionResponse, RejectSolutionResponse
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult


class KnapsackService:
    def __init__(self, http_client: AsyncClient):
        self._client: AsyncClient = http_client

    async def suggest_solution(self, user_id: str, capacity: int, rides: list[KnapsackItem]) -> SuggestedSolution:
        request = KnapsackSolverRequest(items=rides, volume=capacity, knapsack_id=user_id)
        response = await self._client.post("/knapsack-router/solve", json=request.dict())
        response.raise_for_status()

        return SuggestedSolution(**response.json())

    async def accept_solution(self, user_id: str, solution_id: str) -> bool:
        request = AcceptSolutionRequest(solution_id=solution_id, knapsack_id=user_id)
        response = await self._client.post("/knapsack-router/accept-solution", json=request.dict())
        response.raise_for_status()

        response = AcceptSolutionResponse(**response.json())
        return response.result == AcceptResult.ACCEPT_SUCCESS

    async def reject_solutions(self, user_id: str) -> bool:
        request = RejectSolutionsRequest(knapsack_id=user_id)
        response = await self._client.post("/knapsack-router/reject-solutions", json=request.dict())
        response.raise_for_status()

        response = RejectSolutionResponse(**response.json())
        return response.result == RejectResult.REJECT_SUCCESS


async def _usage_example():
    client = AsyncClient(base_url="http://localhost:8001")
    service = KnapsackService(client)

    def _get_random_string():
        return str(uuid4())

    user_id = _get_random_string()

    res = await service.suggest_solution(
        user_id,
        4,
        [
            KnapsackItem(id=_get_random_string(), value=2, volume=1),
            KnapsackItem(id=_get_random_string(), value=2, volume=1),
            KnapsackItem(id=_get_random_string(), value=4, volume=3),
        ],
    )
    accepted = await service.accept_solution(user_id, next(iter(res.solutions.keys())))
    assert accepted

    await service.suggest_solution(
        user_id,
        4,
        [
            KnapsackItem(id=_get_random_string(), value=2, volume=1),
            KnapsackItem(id=_get_random_string(), value=2, volume=1),
            KnapsackItem(id=_get_random_string(), value=4, volume=3),
        ],
    )
    rejected = await service.reject_solutions(user_id)
    assert rejected


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_usage_example())
