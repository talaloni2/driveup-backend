import textwrap
from typing import Optional

from sqlalchemy import text, select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from model.passenger_drive_order import PassengerDriveOrder, PASSENGER_DRIVE_ORDER_TABLE, PassengerDriveOrderStatus

GET_CLOSEST_ORDERS_QUERY = textwrap.dedent(
    f"""

SELECT
    6371 * 2 * ASIN(SQRT(
        POWER(SIN((RADIANS(:latitude) - RADIANS(source_location[1])) / 2), 2) +
        COS(RADIANS(source_location[1])) * COS(RADIANS(:latitude)) *
        POWER(SIN((RADIANS(:longitude) - RADIANS(source_location[2] )) / 2), 2)
    )) AS distance_from_driver, 6371 * 2 * ASIN(SQRT(
        POWER(SIN((RADIANS(dest_location[1]) - RADIANS(source_location[1])) / 2), 2) +
        COS(RADIANS(source_location[1])) * COS(RADIANS(dest_location[1])) *
        POWER(SIN((RADIANS(dest_location[2]) - RADIANS(source_location[2] )) / 2), 2)
    )) AS distance, id, passengers_amount
FROM
    passenger_drive_orders
WHERE
    status ilike '%NEW%'
ORDER BY distance_from_driver

LIMIT 10
"""
)


class PassengerService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, order: PassengerDriveOrder) -> PassengerDriveOrder:
        async with self._session.begin_nested():
            self._session.add(order)

        await self._session.refresh(order)

        return order

    async def get_by_user_email(self, email: str) -> PassengerDriveOrder:
        # async with self._session.begin():
        res = await self._session.execute(
            select(PassengerDriveOrder).where(PassengerDriveOrder.email == email).limit(1)
        )
        return res.scalar_one_or_none()

    async def get_by_order_id(self, order_id: int) -> PassengerDriveOrder:
        res = await self._session.execute(
            select(PassengerDriveOrder).where(PassengerDriveOrder.id == order_id).limit(1)
        )
        return res.scalar_one_or_none()

    async def get_by_order_and_user_id(self, user_id: str, order_id: int) -> PassengerDriveOrder:
        res = await self._session.execute(
            select(PassengerDriveOrder).where(PassengerDriveOrder.email == user_id, PassengerDriveOrder.id == order_id).limit(1)
        )
        return res.scalar_one_or_none()

    async def cancel_order(self, user_id: str, order_id: int) -> bool:
        await self._session.execute(
            delete(PassengerDriveOrder)
            .where(PassengerDriveOrder.email == user_id, PassengerDriveOrder.id == order_id, PassengerDriveOrder.status == PassengerDriveOrderStatus.NEW)
        )
        res = (await self._session.execute(
            select(PassengerDriveOrder)
            .where(PassengerDriveOrder.id == order_id)
        )).scalar_one_or_none()

        is_delete_success = res is None
        return is_delete_success

    async def get_active_by_order_id(self, order_id: int) -> PassengerDriveOrder:
        # async with self._session.begin():
        res = await self._session.execute(
            select(PassengerDriveOrder)
            .where(PassengerDriveOrder.id == order_id, PassengerDriveOrder.status == PassengerDriveOrderStatus.ACTIVE)
            .limit(1)
        )
        return res.scalar_one_or_none()

    async def set_status_to_drive_order(self, order_id: int, new_status: str):
        await self._session.execute(
            update(PassengerDriveOrder).where(PassengerDriveOrder.id == order_id).values(status=new_status)
        )

    async def set_frozen_by(self, order_id: int, freezer_email: str = None):
        if freezer_email:
            # async with self._session.begin():
            await self._session.execute(
                update(PassengerDriveOrder).where((PassengerDriveOrder.id == order_id)).values(frozen_by=freezer_email)
            )

    async def delete(self, drive: PassengerDriveOrder) -> None:
        # async with self._session.begin():
        await self._session.delete(drive)

    async def get_top_order_candidates(self, candidates_amount, current_location: list[float], driver_id: str):
        """
        1) Get x orders
        2) Set them frozen
        """

        # async with self._session.begin():
        results = await self._session.execute(
            text(GET_CLOSEST_ORDERS_QUERY), dict(latitude=current_location[0], longitude=current_location[1])
        )
        orders = results.fetchall()

        for order in orders:
            await self.set_status_to_drive_order(order_id=order.id, new_status="FROZEN")
            await self.set_frozen_by(order_id=order.id, freezer_email=driver_id)

        return orders

    async def release_order_from_freeze(self, email, order_id: int):
        # async with self._session.begin():
        await self._session.execute(
            update(PassengerDriveOrder)
            .where(
                PassengerDriveOrder.status == PassengerDriveOrderStatus.FROZEN,
                PassengerDriveOrder.frozen_by == email,
                PassengerDriveOrder.id == order_id,
            )
            .values(status=PassengerDriveOrderStatus.NEW, frozen_by=None)
        )

    async def release_unchosen_orders_from_freeze(self, email, chosen_order_ids: Optional[list[int]] = None):
        if chosen_order_ids:
            # async with self._session.begin():
            await self._session.execute(
                update(PassengerDriveOrder)
                .where(
                    and_(
                        PassengerDriveOrder.status == PassengerDriveOrderStatus.FROZEN,
                        PassengerDriveOrder.frozen_by == email,
                        PassengerDriveOrder.id.notin_(chosen_order_ids),
                    )
                )
                .values(status=PassengerDriveOrderStatus.NEW, frozen_by=None)
            )
            return

        # async with self._session.begin():
        await self._session.execute(
            update(PassengerDriveOrder)
            .where(
                PassengerDriveOrder.status == PassengerDriveOrderStatus.FROZEN, PassengerDriveOrder.frozen_by == email
            )
            .values(status=PassengerDriveOrderStatus.NEW, frozen_by=None)
        )

    async def delete_all_passenger_drive_order(self):
        await self._session.execute(delete(PassengerDriveOrder))

    async def activate_drive(self, order_id: int, drive_id: str):
        await self._session.execute(
            update(PassengerDriveOrder)
            .where(PassengerDriveOrder.id == order_id)
            .values(status=PassengerDriveOrderStatus.ACTIVE, drive_id=drive_id)
        )
