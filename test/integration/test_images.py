from http import HTTPStatus

import pytest
from httpx import AsyncClient

from model.responses.image_responses import CreateImageResponse, GetImageResponse

pytestmark = pytest.mark.asyncio


async def test_upload_image(test_client: AsyncClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", files={"image": ("Charmander", f)})

    assert resp.status_code == HTTPStatus.OK
    create_resp_body = CreateImageResponse(**resp.json())
    assert create_resp_body.id is not None, "Image should have an ID"
    delete_resp = await test_client.delete(f"/images/{create_resp_body.id}")
    assert delete_resp.status_code == HTTPStatus.OK


async def test_delete_image(test_client: AsyncClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", files={"image": ("Charmander", f)})

    assert resp.status_code == HTTPStatus.OK
    resp_body = CreateImageResponse(**resp.json())
    assert resp_body.id is not None, "Failed creating image"

    del_resp = await test_client.delete(f"/images/{resp_body.id}")
    get_resp = await test_client.get(f"/images/{resp_body.id}")
    assert del_resp.status_code == HTTPStatus.OK, "Image not deleted"
    assert get_resp.status_code == HTTPStatus.NOT_FOUND, "Image delete response was fine but an image still returned"


async def test_delete_non_existing_image(test_client: AsyncClient, ensure_db_schema: None):
    del_resp = await test_client.delete(f"/images/{2**25}")
    assert del_resp.status_code == HTTPStatus.NOT_FOUND, "Image should not be found"


async def test_get_image(test_client: AsyncClient, ensure_db_schema: None):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", files={"image": ("Charmander", f)})

    assert resp.status_code == HTTPStatus.OK
    create_resp_body = CreateImageResponse(**resp.json())
    assert create_resp_body.id is not None, "Image should have an ID"
    get_resp = await test_client.get(f"/images/{create_resp_body.id}")
    assert get_resp.status_code == HTTPStatus.OK
    assert resp.content
    assert isinstance(get_resp.content, bytes)


async def test_get_non_existing_image(test_client: AsyncClient, ensure_db_schema: None):
    get_resp = await test_client.get(f"/images/{2**25}")
    assert get_resp.status_code == HTTPStatus.NOT_FOUND, "Image should not be found"
