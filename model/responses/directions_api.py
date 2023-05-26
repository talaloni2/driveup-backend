from model.base_dto import BaseModel


class DirectionsApiResponse(BaseModel):
    distance_meters: float
    duration_seconds: float
