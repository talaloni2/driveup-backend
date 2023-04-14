from fastapi import APIRouter, UploadFile, Depends

from component_factory import get_image_service
from model.image import Image
from model.responses.image_responses import CreateImageResponse
from service.image_service import ImageService

router = APIRouter()


@router.post("/upload")
async def upload_image(image: UploadFile, image_service: ImageService = Depends(get_image_service)):
    image_data = await image.read()
    image_instance = Image(image_data=image_data, filename=image.filename)

    await image_service.insert_image(image_instance)

    return CreateImageResponse(id=image_instance.id)


