import asyncio
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

from fastapi import HTTPException
from httpx import AsyncClient

from logger import logger
from model.requests.knapsack import KnapsackItem, KnapsackSolverRequest, AcceptSolutionRequest, RejectSolutionsRequest
from model.responses.knapsack import (
    SuggestedSolution,
    AcceptSolutionResponse,
    RejectSolutionResponse,
    ItemClaimedResponse,
)
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult
from service.time_service import TimeService


class KnapsackService:
    def __init__(self, http_client: AsyncClient, time_service: TimeService):
        self._client: AsyncClient = http_client
        self._time_service = time_service

    async def suggest_solution(self, user_id: str, capacity: int, rides: list[KnapsackItem]) -> SuggestedSolution:
        request = KnapsackSolverRequest(items=rides, volume=capacity, knapsack_id=user_id)
        response = await self._client.post("/knapsack-router/solve", json=request.dict())
        if response.status_code not in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.REQUEST_TIMEOUT):
            logger.error(f"Got unexpected status: {response.status_code} from knapsack backend: {response.content}")
            response.raise_for_status()
        elif response.status_code == HTTPStatus.NO_CONTENT:
            return SuggestedSolution(time=self._time_service.now(), solutions={}, expires_at=self._time_service.now())
        elif response.status_code == HTTPStatus.GATEWAY_TIMEOUT:
            raise HTTPException(status_code=HTTPStatus.GATEWAY_TIMEOUT,
                                detail="Got timeout while calculating best drives. Please try again later")

        suggestion = SuggestedSolution(**response.json())
        return suggestion

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

    async def is_ride_request_claimed(self, ride_request_id: str) -> bool:
        response = await self._client.get(f"/knapsack-router/check-claimed/{ride_request_id}")
        response.raise_for_status()

        response = ItemClaimedResponse(**response.json())
        return response.is_claimed


async def _usage_example():
    client = AsyncClient(base_url="http://localhost:8001")
    service = KnapsackService(client, TimeService())

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
