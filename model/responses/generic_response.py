from typing import Optional, TypeVar

from model.base_dto import BaseModel

T = TypeVar("T")


class GenericResponse(BaseModel):
    code: Optional[int]
    status: Optional[str]
    message: Optional[str]
    result: Optional[T]
    detail: Optional[str]
