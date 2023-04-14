from fastapi import FastAPI

from controllers.images import router as images_router

app = FastAPI()

app.include_router(images_router, prefix="/images")
