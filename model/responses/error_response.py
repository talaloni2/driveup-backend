import typing

from starlette.responses import JSONResponse

from model.base_dto import BaseModel


class MessageResponse(BaseModel):
    message: str
