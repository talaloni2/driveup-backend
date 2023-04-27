from http import HTTPStatus

import pytest

from model.requests.rating import RatingRequest
from model.responses.rating import RatingResponse
from test.utils.test_client import TestClient
from test.utils.utils import get_random_email

pytestmart = pytest.mark.asyncio


async def test_post_rating(test_client: TestClient):
    token = await test_client.get_token()
    rating_request = RatingRequest(
        email=get_random_email(),
        rating=1,
    )
    resp = await test_client.post(
        url="/rating",
        req_body=rating_request,
        resp_model=RatingResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert resp.email == rating_request.email
    assert rating_request.rating

    await test_client.delete(
        url=f"/rating/{rating_request.email}",
        headers={'Authorization': f"Bearer {token}"},
    )


async def test_get_rating(test_client: TestClient):
    token = await test_client.get_token()
    rating_request = RatingRequest(
        email=get_random_email(),
        rating=1,
    )
    await test_client.post(
        url="/rating",
        req_body=rating_request,
        resp_model=RatingResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    resp = await test_client.get(
        url=f"/rating/{rating_request.email}",
        resp_model=RatingResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    assert resp.email == rating_request.email
    assert resp.rating == rating_request.rating
    assert resp.total_raters == 1


async def test_delete_rating(test_client: TestClient):
    token = await test_client.get_token()
    rating_request = RatingRequest(
        email=get_random_email(),
        rating=1,
    )
    await test_client.post(
        url="/rating",
        req_body=rating_request,
        resp_model=RatingResponse,
        headers={'Authorization': f"Bearer {token}"},
    )
    await test_client.get(
        url=f"/rating/{rating_request.email}",
        headers={'Authorization': f"Bearer {token}"},
    )
    await test_client.delete(
        url=f"/rating/{rating_request.email}",
        headers={'Authorization': f"Bearer {token}"},
    )
    await test_client.get(
        url=f"/rating/{rating_request.email}",
        assert_status=HTTPStatus.NOT_FOUND,
        headers={'Authorization': f"Bearer {token}"},
    )
