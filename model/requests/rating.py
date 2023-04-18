from model.base_dto import BaseModel


class RatingRequest(BaseModel):
    rating: int
    email: str
