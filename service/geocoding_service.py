import urllib.parse

from httpx import AsyncClient

from model.position import Position, GeocodingResult


class GeocodingService:
    def __init__(self, http_client: AsyncClient, api_key: str):
        self._client: AsyncClient = http_client
        assert api_key, "Request geocoding api key from team member"
        self._api_key = api_key

    def _is_address_urlencoded(self, address: str):
        return urllib.parse.unquote_plus(address) != address

    def normalize_address_query(self, address: str):
        if self._is_address_urlencoded(address):
            return address
        return urllib.parse.quote_plus(address)

    async def geocode_address(self, address: str) -> GeocodingResult:
        # safe_address = urllib.parse.urlencode(address)
        address_query_param = self.normalize_address_query(address)
        resp = await self._client.get(f"/geocode?q={address_query_param}&apiKey={self._api_key}")
        resp.raise_for_status()

        items = resp.json()["items"]
        if not items:
            return None

        return GeocodingResult(
            position=Position(lat=items[0]["position"]["lat"], lon=items[0]["position"]["lng"]),
            is_single_result=len(items) == 1,
        )
