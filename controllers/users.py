import json

import requests
from fastapi import APIRouter, Depends

from component_factory import get_config, get_user_handler_service
from model.configuration import Config
from model.user_schemas import RequestLogin, RequestUser

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/")
async def create(
    request: RequestUser,
    user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.create_user(**json.loads(request.parameter.json()))


@router.get("/")
async def get_users(
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.get_users(token)


@router.get("/{email}")
async def get_user_by_email(
        email: str,
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.get_user_by_email(email, token)


@router.put("/{email}")
async def update_user(
        email: str,
        request: RequestUser,
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    parameters = json.loads(request.parameter.json())
    del parameters["email"]
    return await user_handler_service.update_user(email=email, token=token, **parameters)


@router.delete("/{email}")
async def delete_user(
        email: str,
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.delete_user(email=email, token=token)


@router.get("/validate_token")
async def validate_token(
    token: str = Depends(oauth2_scheme),
    user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.validate_token(token)
