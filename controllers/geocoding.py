import urllib.parse

from fastapi import APIRouter

from service.geocoding_service import GeocodingService

router = APIRouter()


def _is_address_urlencoded(address: str):
    return urllib.parse.unquote(address) != address


@router.get("/")
async def geocode_address(address: str, geocoding_service: GeocodingService):
    if not _is_address_urlencoded(address):
        address = urllib.parse.urlencode(address)
    return geocoding_service.geocode_address(address)
