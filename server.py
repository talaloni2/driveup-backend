from fastapi import FastAPI

from controllers.images import router as images_router
from controllers.rating import router as rating_router
from controllers.users import router as users_router
from controllers.users_map import router as users_map_router

app = FastAPI()

app.include_router(images_router, prefix="/images")
app.include_router(rating_router, prefix="/rating")
app.include_router(images_router, prefix="/images", tags=["images"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(users_map_router, prefix="/users_map", tags=["users_map"])
