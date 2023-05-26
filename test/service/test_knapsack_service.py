from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, Response, Request, HTTPStatusError

from model.requests.knapsack import KnapsackItem
from model.responses.knapsack import SuggestedSolution, AcceptSolutionResponse, RejectSolutionResponse, \
    KnapsackSolution, ItemClaimedResponse
from model.suggested_solutions_actions_statuses import AcceptResult, RejectResult
from service.knapsack_service import KnapsackService
from service.time_service import TimeService
from test.utils.utils import get_random_email, get_random_string


pytestmark = pytest.mark.asyncio


def _get_response(json: str, status: int = HTTPStatus.OK) -> Response:
    request_mock = MagicMock(Request)
    request_mock.url = "mock"
    return Response(text=json, status_code=status, request=request_mock)


async def test_suggest_solution():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    item = KnapsackItem(id=get_random_string(), value=2, volume=1)
    solutions = {get_random_string(): KnapsackSolution(algorithm="aaa", items=[item])}
    client.post = AsyncMock(
        return_value=_get_response(SuggestedSolution(time=datetime.now(), solutions=solutions, expires_at=datetime.now()).json())
    )

    result = await service.suggest_solution(get_random_email(), 1, [item])
    assert result.solutions == solutions


async def test_suggest_solution_error():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(return_value=_get_response("", HTTPStatus.INTERNAL_SERVER_ERROR))

    with pytest.raises(HTTPStatusError):
        await service.suggest_solution(get_random_email(), 1, [KnapsackItem(id=get_random_string(), value=2, volume=1)])


async def test_accept_solution():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(
        return_value=_get_response(AcceptSolutionResponse(result=AcceptResult.ACCEPT_SUCCESS).json())
    )

    accepted = await service.accept_solution(get_random_email(), get_random_string())
    assert accepted


async def test_accept_solution_invalid():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(return_value=_get_response(AcceptSolutionResponse(result=AcceptResult.CLAIM_FAILED).json()))

    accepted = await service.accept_solution(get_random_email(), get_random_string())
    assert not accepted


async def test_accept_solution_error():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(return_value=_get_response("", HTTPStatus.INTERNAL_SERVER_ERROR))

    with pytest.raises(HTTPStatusError):
        await service.accept_solution(get_random_email(), get_random_string())


async def test_reject_solution():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(
        return_value=_get_response(RejectSolutionResponse(result=RejectResult.REJECT_SUCCESS).json())
    )

    rejected = await service.reject_solutions(get_random_email())
    assert rejected


async def test_reject_solution_invalid():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(return_value=_get_response(RejectSolutionResponse(result=RejectResult.CLAIM_FAILED).json()))

    rejected = await service.reject_solutions(get_random_email())
    assert not rejected


async def test_reject_solution_error():
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.post = AsyncMock(return_value=_get_response("", HTTPStatus.INTERNAL_SERVER_ERROR))

    with pytest.raises(HTTPStatusError):
        await service.reject_solutions(get_random_email())


@pytest.mark.parametrize("is_claimed", [True, False])
async def test_is_item_claimed(is_claimed):
    client = AsyncMock(AsyncClient)
    service = KnapsackService(client, TimeService())
    client.get = AsyncMock(
        return_value=_get_response(ItemClaimedResponse(is_claimed=is_claimed).json())
    )

    is_claimed_response = await service.is_ride_request_claimed(get_random_string())
    assert is_claimed_response == is_claimed
