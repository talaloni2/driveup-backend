from fastapi import APIRouter, Depends

from component_factory import get_geocoding_service
from service.geocoding_service import GeocodingService

router = APIRouter()


@router.get("")
async def geocode_address(
        address: str,
        geocoding_service: GeocodingService = Depends(get_geocoding_service),
        ):
    return await geocoding_service.geocode_address(address)
