from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from component_factory import get_user_handler_service
from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login")
@router.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    login = await user_handler_service.login(username=form_data.username, password=form_data.password)
    if not login:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return login
