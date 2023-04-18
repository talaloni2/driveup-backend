from model.base_dto import BaseModel


class RatingResponse(BaseModel):
    email: str
    rating: float
    total_raters: int
