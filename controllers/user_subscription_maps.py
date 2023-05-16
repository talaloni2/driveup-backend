import json

import requests
from fastapi import APIRouter, Depends, HTTPException

from component_factory import get_config, get_user_handler_service, get_subscription_handler_service
from model.configuration import Config

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from model.user_subscription_map_schemas import RequestUserSubscriptionMap
from service.subscription_handler_service import SubscriptionHandlerService
from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def get_user_subscription_maps(
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    response = await subscription_handler_service.get_user_subscription_maps()
    if response.code != 200:
        raise HTTPException(status_code=response.code, detail=response.detail)

    return response


@router.post("/")
async def create_user_subscription_map(
        request: RequestUserSubscriptionMap,
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    response = await subscription_handler_service.create_user_subscription_map(**json.loads(request.parameter.json()))
    if response.code != 200:
        raise HTTPException(status_code=response.code, detail=response.detail)

    return response


@router.get("/{user_email}/{subscription_name}")
async def get_user_subscription_map(
        user_email: str,
        subscription_name: str,
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    response = await subscription_handler_service.get_user_subscription_map(email=user_email, name=subscription_name)
    if response.code != 200:
        raise HTTPException(status_code=response.code, detail=response.detail)

    return response


@router.delete("/{user_email}/{subscription_name}")
async def delete_user_subscription_map(
        user_email: str,
        subscription_name: str,
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    response = await subscription_handler_service.delete_user_subscription_map(email=user_email, name=subscription_name)
    if response.code != 200:
        raise HTTPException(status_code=response.code, detail=response.detail)

    return response
