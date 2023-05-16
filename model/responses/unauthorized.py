from typing import Optional

from model.base_dto import BaseModel
from model.responses.generic_response import GenericResponse


class UnauthorizedResponse(GenericResponse):
    result: None
    detail: str = "Unauthorized"
