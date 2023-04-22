import urllib.parse

from httpx import AsyncClient

from model.position import Position, GeocodingResult


class GeocodingService:
    def __init__(self, http_client: AsyncClient, api_key: str):
        self._client: AsyncClient = http_client
        assert api_key, "Request geocoding api key from team member"
        self._api_key = api_key

    async def geocode_address(self, address: str) -> GeocodingResult:
        # safe_address = urllib.parse.urlencode(address)
        resp = await self._client.get(f"/geocode?q={address}&apiKey={self._api_key}")
        resp.raise_for_status()

        items = resp.json()["items"]
        if not items:
            return None

        return GeocodingResult(position=Position(lat=items[0]["position"]["lat"], lon=items[0]["position"]["lng"]),
                               is_single_result=len(items) == 1)
