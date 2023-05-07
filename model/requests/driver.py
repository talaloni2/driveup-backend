from model.base_dto import BaseModel


class DriverOrderDrive(BaseModel):
    user_id: int
    current_location: str


class DriverAcceptDrive(BaseModel):
    user_id: int
    solution_id: int


class DriverRejectDrive(BaseModel):
    user_id: int
    solution_id: int