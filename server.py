from fastapi import FastAPI

from controllers.images import router as images_router
from controllers.rating import router as rating_router

app = FastAPI()

app.include_router(images_router, prefix="/images")
app.include_router(rating_router, prefix="/rating")
