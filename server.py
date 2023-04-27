from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from component_factory import get_user_handler_service
from controllers.images import router as images_router
from controllers.rating import router as rating_router
from controllers.users import router as users_router
from controllers.users_map import router as users_map_router
from controllers.geocoding import router as geocoding_router
from service.user_handler_service import UserHandlerService

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    return await user_handler_service.login(username=form_data.username, password=form_data.password)


app.include_router(rating_router, prefix="/rating", tags=["rating"])
app.include_router(images_router, prefix="/images", tags=["images"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(users_map_router, prefix="/users_map", tags=["users_map"])
app.include_router(geocoding_router, prefix="/geocode", tags=["geocode"])
