import asyncio
import json
from http import HTTPStatus
from unittest.mock import MagicMock

from fastapi import HTTPException
from httpx import AsyncClient

from model.responses.directions_api import DirectionsApiResponse
from model.responses.geocode import Geocode


def _get_example_directions():
    with open("directions_response_example.json") as f:
        return json.load(f)


class DirectionsService:
    def __init__(self, directions_api_key: str, http_client: AsyncClient):
        self._directions_api_url_pattern: str = f"https://api.openrouteservice.org/v2/directions/driving-car"
        self._client: AsyncClient = http_client
        self._api_key: str = directions_api_key

    async def get_directions(self, source: Geocode, destination: Geocode) -> DirectionsApiResponse:
        api_resp = await self._call_directions_api(source, destination)
        summary = api_resp["features"][0]["properties"]["summary"]
        return DirectionsApiResponse(distance_meters=summary["distance"], duration_seconds=summary["duration"])

    async def _call_directions_api(self, source: Geocode, destination: Geocode) -> dict:
        resp = await self._client.get(
            self._directions_api_url_pattern,
            params={
                "api_key": self._api_key,
                "start": f"{source.longitude},{source.latitude}",
                "end": f"{destination.longitude},{destination.latitude}",
            },
        )
        if resp.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail={"message": "Encountered error in directions api"}
            )
        return resp.json()
