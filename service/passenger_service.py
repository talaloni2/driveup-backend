import textwrap

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.drive_order import DriveOrder, DRIVE_ORDER_TABLE

SAVE_RATING_QUERY_TEMPLATE = textwrap.dedent(
    f"""
INSERT INTO {DRIVE_ORDER_TABLE} (email, passengers_amount, status, source_location, dest_location)
VALUES (:email, :passengers_amount, :status, :source_location, :dest_location)
"""
)


class PassengerService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, order: DriveOrder) -> DriveOrder:
        params = {"email": order.email, "passengers_amount": order.passengers_amount, "status": "NEW",
                  "source_location": [order.source_location.lat, order.source_location.lon],
                  "dest_location": [order.dest_location.lat, order.dest_location.lon]}

        async with self._session.begin():
            await self._session.execute(text(SAVE_RATING_QUERY_TEMPLATE), params=params)

        return await self.get_by_user_email(order.email)

    async def get_by_user_email(self, email: str) -> DriveOrder:
        async with self._session.begin():
            res = await self._session.execute(select(DriveOrder).where(DriveOrder.email == email).limit(1))
        return res.scalar_one_or_none()

    async def get_by_order_id(self, order_id: int) -> DriveOrder:
        async with self._session.begin():
            res = await self._session.execute(select(DriveOrder).where(DriveOrder.id == order_id).limit(1))
        return res.scalar_one_or_none()

    async def delete(self, drive: DriveOrder) -> None:
        async with self._session.begin():
            await self._session.delete(drive)
