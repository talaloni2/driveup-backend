from model.base_dto import BaseModel


class CreateImageResponse(BaseModel):
    id: int


class GetImageResponse(BaseModel):
    id: int
    data: bytes
    file_name: str
