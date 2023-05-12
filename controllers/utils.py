from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from component_factory import get_user_handler_service
from model.base_dto import BaseModel
from service.user_handler_service import UserHandlerService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticatedUser(BaseModel):
    email: str


async def authenticated_user(
    token: str = Depends(oauth2_scheme), user_handler_service: UserHandlerService = Depends(get_user_handler_service)
) -> AuthenticatedUser:
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return AuthenticatedUser(**is_token_valid.result["token"])
