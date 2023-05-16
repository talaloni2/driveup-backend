import json

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from component_factory import get_user_handler_service
from model.user_schemas import RequestUser
from service.user_handler_service import UserHandlerService
from controllers.utils import authenticated_user, AuthenticatedUser

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
        auth_user: AuthenticatedUser = Depends(authenticated_user),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.get_users(auth_user.token)


@router.put("/update")
async def update_user(
        request: RequestUser,
        auth_user: AuthenticatedUser = Depends(authenticated_user),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    parameters = json.loads(request.parameter.json())
    del parameters["email"]
    return await user_handler_service.update_user(email=auth_user.email, token=auth_user.token, **parameters)


@router.delete("/delete")
async def delete_user(
        auth_user: AuthenticatedUser = Depends(authenticated_user),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.delete_user(email=auth_user.email, token=auth_user.token)


@router.get("/validate_token")
async def validate_token(
    auth_user: AuthenticatedUser = Depends(authenticated_user),
    user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.validate_token(auth_user.token)


@router.get("/{email}")
async def get_user_by_email(
        email: str,
        auth_user: AuthenticatedUser = Depends(authenticated_user),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.get_user_by_email(email, auth_user.token)
