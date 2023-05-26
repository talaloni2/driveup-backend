from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.driver_drive_order import DriverDriveOrder, DriveOrderStatus
from model.responses.knapsack import SuggestedSolution


class DriverService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_suggestions(self, driver_id: str, suggestions: SuggestedSolution):
        suggestions = [
            DriverDriveOrder(
                id=sid,
                driver_id=driver_id,
                expires_at=suggestions.expires_at,
                passengers_amount=s.total_volume,
                passenger_orders=[i.dict() for i in s.items],
                status=DriveOrderStatus.PENDING
            )
            for sid, s in suggestions.solutions.items()
        ]
        # async with self._session.begin():
        self._session.add_all(suggestions)

    async def get_suggestion(self, driver_id: str, suggestion_id: str) -> DriverDriveOrder:
        res = await self._session.execute(select(DriverDriveOrder).where(DriverDriveOrder.driver_id == driver_id, DriverDriveOrder.id == suggestion_id))
        return res.scalar_one_or_none()

    async def reject_solutions(self, driver_id: str):
        await self._session.execute(delete(DriverDriveOrder).where(DriverDriveOrder.driver_id == driver_id,
                                                                   DriverDriveOrder.status == DriveOrderStatus.PENDING))

    async def drop_table_driver_drive_order(self):
        await self._session.execute(delete(DriverDriveOrder))
