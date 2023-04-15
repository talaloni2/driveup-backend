from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from model.requests.rating import RatingRequest
from model.responses.error_response import MessageResponse

router = APIRouter()


@router.post("")
async def rate_user(rating: RatingRequest):
    if rating.rating < 0 or rating.rating > 5:
        return JSONResponse(MessageResponse(message="Rating should be between 0 to 5").json(), status_code=HTTPStatus.BAD_REQUEST)

