from http import HTTPStatus

import pytest

from model.requests.rating import RatingRequest
from model.responses.rating import RatingResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio


async def test_post_rating(test_client: TestClient):
    rating_request = RatingRequest(email=get_random_email(), rating=1)
    resp = await test_client.post("/rating", rating_request, RatingResponse)
    assert resp.email == rating_request.email
    assert rating_request.rating

    await test_client.delete(f"/rating/{rating_request.email}")


async def test_get_rating(test_client: TestClient):
    rating_request = RatingRequest(email=get_random_email(), rating=1)
    await test_client.post("/rating", rating_request, RatingResponse)
    resp = await test_client.get(f"/rating/{rating_request.email}", RatingResponse)
    assert resp.email == rating_request.email
    assert resp.rating == rating_request.rating
    assert resp.total_raters == 1


async def test_delete_rating(test_client: TestClient):
    rating_request = RatingRequest(email=get_random_email(), rating=1)
    await test_client.post("/rating", rating_request, RatingResponse)
    await test_client.get(f"/rating/{rating_request.email}")
    await test_client.delete(f"/rating/{rating_request.email}")
    await test_client.get(f"/rating/{rating_request.email}", assert_status=HTTPStatus.NOT_FOUND)
