import asyncio
import json
from unittest.mock import MagicMock

from httpx import AsyncClient

from model.responses.directions_api import DirectionsApiResponse
from model.responses.geocode import Geocode


def _get_example_directions():
    with open("directions_response_example.json") as f:
        return json.load(f)


class DirectionsService:
    def __init__(self, directions_api_key: str, http_client: AsyncClient):
        self._directions_api_url_pattern: str = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={directions_api_key}&start={{start_lon}},{{start_lat}}&end={{end_lon}},{{end_lat}}"
        self._client: AsyncClient = http_client
        self._api_key: str = directions_api_key

    async def get_directions(self, source: Geocode, destination: Geocode) -> DirectionsApiResponse:
        api_resp = await self._call_directions_api()
        summary = api_resp["features"][0]["properties"]["summary"]
        return DirectionsApiResponse(distance_meters=summary["distance"], duration_seconds=summary["duration"])

    async def _call_directions_api(self) -> dict:
        return _get_example_directions()


if __name__ == '__main__':
    print(asyncio.new_event_loop().run_until_complete(DirectionsService("mock", MagicMock(), "").get_directions(None, None)))