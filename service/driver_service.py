from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from model.driver_drive_order import DriverDriveOrder, DriveOrderStatus
from model.passenger_drive_order import PassengerDriveOrder
from model.responses.knapsack import SuggestedSolution
from service.passenger_service import PassengerService


class DriverService:
    def __init__(self, session: AsyncSession, passenger_service: PassengerService):
        self._session = session
        self._passenger_service: PassengerService = passenger_service

    async def save_suggestions(self, driver_id: str, suggestions: SuggestedSolution, current_location: List[float]):
        suggestions = [
            DriverDriveOrder(
                id=sid,
                driver_id=driver_id,
                expires_at=suggestions.expires_at,
                passengers_amount=s.total_volume,
                passenger_orders=[i.dict() for i in s.items],
                status=DriveOrderStatus.PENDING,
                time=suggestions.time,
                algorithm=s.algorithm,
                current_location=current_location
            )
            for sid, s in suggestions.solutions.items()
        ]
        self._session.add_all(suggestions)

    async def get_suggestion(self, driver_id: str, suggestion_id: str) -> DriverDriveOrder:
        res = await self._session.execute(
            select(DriverDriveOrder).where(
                DriverDriveOrder.driver_id == driver_id, DriverDriveOrder.id == suggestion_id
            )
        )
        return res.scalar_one_or_none()

    async def reject_solutions(self, driver_id: str):
        async with self._session.begin_nested():
            await self._passenger_service.release_unchosen_orders_from_freeze(driver_id, [])
            await self._session.execute(
                delete(DriverDriveOrder).where(
                    DriverDriveOrder.driver_id == driver_id, DriverDriveOrder.status == DriveOrderStatus.PENDING
                )
            )

    async def get_suggestions(self, driver_id: str) -> list[DriverDriveOrder]:
        return [
            a[0]
            for a in await self._session.execute(
                select(DriverDriveOrder).where(
                    DriverDriveOrder.driver_id == driver_id, DriverDriveOrder.status == DriveOrderStatus.PENDING
                )
            )
        ]

    async def delete_all_driver_drive_orders(self):
        await self._session.execute(delete(DriverDriveOrder))

    async def get_driver_drive_by_id(self, drive_id) -> DriverDriveOrder:
        res = await self._session.execute(select(DriverDriveOrder).where(
                DriverDriveOrder.id == drive_id,
            ))
        return res.scalar_one_or_none()

    async def set_drive_status(self, drive_id: str, status: DriveOrderStatus):
        async with self._session.begin_nested():
            await self._session.execute(update(DriverDriveOrder).where(DriverDriveOrder.id == drive_id).values(status=status))
