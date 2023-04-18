import requests
from fastapi import APIRouter, Depends

from component_factory import get_config
from model.configuration import Config
from model.user_schemas import RequestLogin, RequestUser

router = APIRouter()


@router.post("/login")
async def login(request: RequestLogin, config: Config = Depends(get_config)):
    return requests.post(f"{config.users_handler_base_url}/users/login", data=request.json()).json()


@router.post("/")
async def create(request: RequestUser, config: Config = Depends(get_config)):
    return requests.post(f"{config.users_handler_base_url}/users/", data=request.json()).json()
