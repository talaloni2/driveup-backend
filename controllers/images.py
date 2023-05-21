from http import HTTPStatus

from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import JSONResponse, Response

from component_factory import get_image_service, get_image_normalization_service
from controllers.utils import AuthenticatedUser, authenticated_user
from model.image import Image
from model.responses.error_response import MessageResponse
from model.responses.image_responses import CreateImageResponse
from service.image_normalization_service import ImageNormalizationService
from service.image_service import ImageService

router = APIRouter()


@router.post("/upload")
async def upload_image(
    image: UploadFile,
    image_service: ImageService = Depends(get_image_service),
    normalizer: ImageNormalizationService = Depends(get_image_normalization_service),
    user: AuthenticatedUser = Depends(authenticated_user),
) -> CreateImageResponse:
    image_data = normalizer.normalize(await image.read())
    image_instance = Image(image_data=image_data, filename=normalizer.normalize_file_name(image.filename), related_email=user.email)

    await delete_image(image_service, user)
    await image_service.insert(image_instance)

    return CreateImageResponse(id=image_instance.id)


@router.delete("/")
async def delete_image(
    image_service: ImageService = Depends(get_image_service),
    user: AuthenticatedUser = Depends(authenticated_user),
):
    img = await image_service.get_by_email(user.email)
    if not img:
        return JSONResponse(MessageResponse(message="Image not found").json(), status_code=HTTPStatus.NOT_FOUND)

    await image_service.delete(img)
    return MessageResponse(message="Success")


@router.get("/{id}")
async def get_image_by_id(
    id: int,
    image_service: ImageService = Depends(get_image_service),
):
    img = await image_service.get(id)
    if not img:
        return JSONResponse(MessageResponse(message="Image not found").json(), status_code=HTTPStatus.NOT_FOUND)

    return Response(
        content=img.image_data,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{img.filename}"'},
    )
