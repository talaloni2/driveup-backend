from fastapi import FastAPI, Depends

from controllers.geocoding import router as geocoding_router
from controllers.images import router as images_router
from controllers.login import router as login_router
from controllers.passenger import router as passenger_router
from controllers.rating import router as rating_router
from controllers.driver import router as driver_router

from controllers.users import router as users_router
from controllers.users_map import router as users_map_router
from controllers.utils import authenticated_user

app = FastAPI()


app.include_router(rating_router, prefix="/rating", tags=["rating"], dependencies=[Depends(authenticated_user)])
app.include_router(images_router, prefix="/images", tags=["images"], dependencies=[Depends(authenticated_user)])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(
    users_map_router, prefix="/users_map", tags=["users_map"], dependencies=[Depends(authenticated_user)]
)
app.include_router(geocoding_router, prefix="/geocode", tags=["geocode"], dependencies=[Depends(authenticated_user)])
app.include_router(login_router, tags=["users"])
app.include_router(passenger_router, prefix="/passenger", tags=["passenger"], dependencies=[Depends(authenticated_user)])
app.include_router(driver_router, prefix="/driver", tags=["driver"], dependencies=[Depends(authenticated_user)])


