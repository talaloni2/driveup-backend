from http import HTTPStatus

import pytest
from httpx import AsyncClient

from model.responses.image_responses import CreateImageResponse


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ['asyncio'])
async def test_upload_image(test_client: AsyncClient, ensure_db_schema: None, anyio_backend):
    with open("test/resources/image-upload.png", mode="rb") as f:
        resp = await test_client.post("/images/upload", files={"image": ("Charmander", f)})

    assert resp.status_code == HTTPStatus.OK
    resp_body = CreateImageResponse(**resp.json())
    assert resp_body.id is not None, "Image should have an ID"
    # TODO: delete the image when image deletion is available

