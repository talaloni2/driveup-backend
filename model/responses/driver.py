from model.base_dto import BaseModel

from model.requests.knapsack import KnapsackItem


class DriverSuggestedDrives(BaseModel):
    driver_id: int
    suggested_drives: list[KnapsackItem]

#
# class DriverGetDriveResponse(BaseModel):
#     drive_id: int