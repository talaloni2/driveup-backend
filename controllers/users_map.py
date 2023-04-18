import requests
from fastapi import APIRouter, Depends

from component_factory import get_config
from model.configuration import Config
from model.user_schemas import RequestLogin, RequestUser

router = APIRouter()


@router.get("/{user_email}")
async def get_by_user_email(user_email: str, config: Config = Depends(get_config)):
    return requests.get(f"{config.subscriptions_handler_base_url}/users_map/{user_email}").json()
