import requests
from fastapi import APIRouter, Depends, HTTPException

from component_factory import get_config, get_user_handler_service, get_subscription_handler_service
from model.configuration import Config

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from service.subscription_handler_service import SubscriptionHandlerService
from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/{user_email}")
async def get_by_user_email(
        email: str,
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await subscription_handler_service.get_by_user_email(email=email)
