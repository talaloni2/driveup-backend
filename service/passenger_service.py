import textwrap

from sqlalchemy import text, select, update
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

        async with self._session.begin():
            self._session.add(order)

        await self._session.refresh(order)

        return order

    async def get_by_user_email(self, email: str) -> DriveOrder:
        async with self._session.begin():
            res = await self._session.execute(select(DriveOrder).where(DriveOrder.email == email).limit(1))
        return res.scalar_one_or_none()

    async def get_by_order_id(self, order_id: int) -> DriveOrder:
        async with self._session.begin():
            res = await self._session.execute(select(DriveOrder).where(DriveOrder.id == order_id, DriveOrder.status == "ACTIVE").limit(1))
        return res.scalar_one_or_none()

    async def set_status_to_drive_order(self, order_id: int, new_status: str) -> DriveOrder:
        #async with self._session.begin():
        await self._session.execute(update(DriveOrder).where((DriveOrder.id == order_id)).values(status=new_status))

    async def set_frozen_by(self, order_id: int, freezer_email: str = None) -> DriveOrder:
        #async with self._session.begin():
        if freezer_email:
            await self._session.execute(update(DriveOrder).where((DriveOrder.id == order_id)).values(frozen_by=freezer_email))

    async def delete(self, drive: DriveOrder) -> None:
        async with self._session.begin():
            await self._session.delete(drive)

    async def get_top_order_candidates(self, candidates_amount, current_location ):
        """
        1) Get x orders
        2) Set them frozen
        """
        res = await self._session.execute(
            select(DriveOrder).where(DriveOrder.status == "NEW").limit(candidates_amount))
        orders = res.scalars().all()

        for order in orders:
            await self.set_status_to_drive_order(order_id=order.id, new_status="FROZEN")

        return orders

    async def release_unchosen_orders_from_freeze(self, email, chosen_order_id=None):
        if chosen_order_id:
            await self._session.execute(update(DriveOrder).where((DriveOrder.status == "FROZEN", DriveOrder.frozen_by == email,
                                         DriveOrder.id != chosen_order_id)).values(status="NEW"))
            return

        await self._session.execute(
            update(DriveOrder).where((DriveOrder.status == "FROZEN", DriveOrder.frozen_by == email)).values(status="NEW"))









