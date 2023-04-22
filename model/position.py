from model.base_dto import BaseModel


class Position(BaseModel):
    lat: float
    lon: float


class GeocodingResult(BaseModel):
    position: Position
    is_single_result: bool
