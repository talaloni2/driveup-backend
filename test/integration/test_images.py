from http import HTTPStatus

import pytest

from model.responses.image_responses import CreateImageResponse
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio


async def test_upload_image(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post(
            url="/images/upload",
            req_body=None,
            resp_model=CreateImageResponse,
            files={"image": ("Charmander", f)},
            headers={'Authorization': f"Bearer {token}"},
        )

    assert resp.id is not None, "Image should have an ID"
    await test_client.delete(
        url=f"/images/{resp.id}",
        resp_model=None,
        headers={'Authorization': f"Bearer {token}"},
    )


async def test_delete_image(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post(
            url="/images/upload",
            req_body=None,
            resp_model=CreateImageResponse,
            files={"image": ("Charmander", f)},
            headers={'Authorization': f"Bearer {token}"},
        )

    assert resp.id is not None, "Failed creating image"

    await test_client.delete(
        url=f"/images/{resp.id}",
        headers={'Authorization': f"Bearer {token}"},
    )
    await test_client.get(
        url=f"/images/{resp.id}",
        assert_status=HTTPStatus.NOT_FOUND,
        headers={'Authorization': f"Bearer {token}"},
    )


async def test_delete_non_existing_image(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    await test_client.delete(
        url=f"/images/{2 ** 25}",
        assert_status=HTTPStatus.NOT_FOUND,
        headers={'Authorization': f"Bearer {token}"},
    )


async def test_get_image(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post(
            url="/images/upload",
            req_body=None,
            resp_model=CreateImageResponse,
            files={"image": ("Charmander", f)},
            headers={'Authorization': f"Bearer {token}"},
        )

    assert resp.id is not None, "Image should have an ID"
    get_resp = await test_client.get(
        url=f"/images/{resp.id}",
        headers={'Authorization': f"Bearer {token}"},
    )
    assert isinstance(get_resp.content, bytes)


async def test_get_non_existing_image(test_client: TestClient, ensure_db_schema: None):
    token = await test_client.get_token()
    await test_client.get(
        url=f"/images/{2 ** 25}",
        assert_status=HTTPStatus.NOT_FOUND,
        headers={'Authorization': f"Bearer {token}"},
    )
