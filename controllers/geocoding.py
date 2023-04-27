import urllib.parse

from fastapi import APIRouter, Depends, HTTPException

from component_factory import get_geocoding_service, get_user_handler_service
from service.geocoding_service import GeocodingService
from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("")
async def geocode_address(
        address: str,
        geocoding_service: GeocodingService = Depends(get_geocoding_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service)):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # if not _is_address_urlencoded(address):
    #     address = urllib.parse.urlencode(address)
    return await geocoding_service.geocode_address(address)
