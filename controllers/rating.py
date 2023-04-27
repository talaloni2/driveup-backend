from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from component_factory import get_rating_service, get_user_handler_service
from model.requests.rating import RatingRequest
from model.responses.error_response import MessageResponse
from model.responses.rating import RatingResponse
from model.user_rating import UserRating
from service.rating_service import RatingService

from fastapi.security import OAuth2PasswordBearer

from service.user_handler_service import UserHandlerService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _to_rating_response(rating: UserRating):
    return RatingResponse(email=rating.email, rating=rating.rating, total_raters=rating.raters_count)


@router.post("")
async def rate_user(
        rating: RatingRequest,
        rating_service: RatingService = Depends(get_rating_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if rating.rating < 0 or rating.rating > 5:
        return JSONResponse(
            MessageResponse(message="Rating should be between 0 to 5").json(), status_code=HTTPStatus.BAD_REQUEST
        )

    # TODO: Add validation for rated user existance.

    db_rating = UserRating(email=rating.email, rating=rating.rating, raters_count=1)
    final_rating = await rating_service.save(db_rating)
    return _to_rating_response(final_rating)


@router.get("/{email}")
async def get_user_rating(
        email: str,
        rating_service: RatingService = Depends(get_rating_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    rating = await rating_service.get_by_email(email)
    if not rating:
        return JSONResponse(MessageResponse(message="User not found").json(), status_code=HTTPStatus.NOT_FOUND)

    return _to_rating_response(rating)


@router.delete("/{email}")
async def delete_user_rating(
        email: str,
        rating_service: RatingService = Depends(get_rating_service),
        token: str = Depends(oauth2_scheme),
        user_handler_service: UserHandlerService = Depends(get_user_handler_service),
):
    is_token_valid = await user_handler_service.validate_token(token)
    if is_token_valid.code != 200 or is_token_valid.result["is_valid"] is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")

    rating = await rating_service.get_by_email(email)
    if not rating:
        return JSONResponse(MessageResponse(message="User not found").json(), status_code=HTTPStatus.NOT_FOUND)

    await rating_service.delete(rating)
    return MessageResponse(message="Success")
