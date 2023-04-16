from http import HTTPStatus

import pytest

from model.responses.image_responses import CreateImageResponse
from test.utils.test_client import TestClient

pytestmark = pytest.mark.asyncio


async def test_upload_image(test_client: TestClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", None, CreateImageResponse, files={"image": ("Charmander", f)})

    assert resp.id is not None, "Image should have an ID"
    await test_client.delete(f"/images/{resp.id}", None)


async def test_delete_image(test_client: TestClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", None, CreateImageResponse, files={"image": ("Charmander", f)})

    assert resp.id is not None, "Failed creating image"

    await test_client.delete(f"/images/{resp.id}")
    await test_client.get(f"/images/{resp.id}", assert_status=HTTPStatus.NOT_FOUND)


async def test_delete_non_existing_image(test_client: TestClient, ensure_db_schema: None):
    await test_client.delete(f"/images/{2**25}", assert_status=HTTPStatus.NOT_FOUND)


async def test_get_image(test_client: TestClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", None, CreateImageResponse, files={"image": ("Charmander", f)})

    assert resp.id is not None, "Image should have an ID"
    get_resp = await test_client.get(f"/images/{resp.id}")
    assert isinstance(get_resp, bytes)


async def test_get_non_existing_image(test_client: TestClient, ensure_db_schema: None):
    await test_client.get(f"/images/{2**25}", assert_status=HTTPStatus.NOT_FOUND)
