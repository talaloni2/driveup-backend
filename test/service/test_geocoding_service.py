import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from model.position import Position
from service.geocoding_service import GeocodingService

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "address,result",
    [["Maiden lane 75 new york", "Maiden+lane+75+new+york"], ["Maiden+lane+75+new+york", "Maiden+lane+75+new+york"]],
)
def test_address_urlencoding(address, result):
    res = GeocodingService(AsyncMock(), "mock").normalize_address_query(address)
    assert res == result


async def test_geocoding_service():
    client = AsyncMock(AsyncClient)
    with open("test/resources/geocoding-response.json", mode="r") as f:
        resp = json.load(f)
    resp_mock = AsyncMock()
    resp_mock.raise_for_status = MagicMock()
    resp_mock.json = MagicMock(return_value=resp)
    client.get = AsyncMock(return_value=resp_mock)

    res = await GeocodingService(client, "mock").geocode_address("test_address")
    expected_position = Position(lat=resp["items"][0]["position"]["lat"], lon=resp["items"][0]["position"]["lng"])
    assert res.position == expected_position
    assert not res.is_single_result
