from http import HTTPStatus

from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse, Response

from component_factory import get_image_service, get_image_normalization_service, get_user_handler_service
from model.image import Image
from model.responses.error_response import MessageResponse
from model.responses.image_responses import CreateImageResponse
from service.image_normalization_service import ImageNormalizationService
from service.image_service import ImageService

from fastapi.security import OAuth2PasswordBearer

from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/upload")
async def upload_image(
        image: UploadFile,
        image_service: ImageService = Depends(get_image_service),
        normalizer: ImageNormalizationService = Depends(get_image_normalization_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    image_data = normalizer.normalize(await image.read())
    image_instance = Image(image_data=image_data, filename=normalizer.normalize_file_name(image.filename))

    await image_service.insert_image(image_instance)

    return CreateImageResponse(id=image_instance.id)


@router.delete("/{id}")
async def delete_image(
        id: int,
        image_service: ImageService = Depends(get_image_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    img = await image_service.get_image(id)
    if not img:
        return JSONResponse(MessageResponse(message="Image not found").json(), status_code=HTTPStatus.NOT_FOUND)

    await image_service.delete_image(img)
    return MessageResponse(message="Success")


@router.get("/{id}")
async def get_image_by_id(
        id: int,
        image_service: ImageService = Depends(get_image_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    img = await image_service.get_image(id)
    if not img:
        return JSONResponse(MessageResponse(message="Image not found").json(), status_code=HTTPStatus.NOT_FOUND)

    return Response(
        content=img.image_data,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{img.filename}"'},
    )
