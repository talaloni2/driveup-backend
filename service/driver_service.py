# import textwrap
#
# from sqlalchemy import text, select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from model.drive_order import DriveOrder, DRIVE_ORDER_TABLE
#
# SAVE_RATING_QUERY_TEMPLATE = textwrap.dedent(f"""
# INSERT INTO {DRIVE_ORDER_TABLE} (user_id, passengers_amount, status, source_location, dest_location)
# VALUES (:user_id, :passengers_amount, "NEW", :source_location, :dest_location)
# """
# )
#
#
# class DriverService:
#     def __init__(self, session: AsyncSession):
#         self._session = session
#
#     async def save(self, order: DriveOrder) -> DriveOrder:
#         params = {"user_id": order.user_id, "passengers_amount": order.passengers_amount,
#                   "source_location": order.source_location,
#                   "dest_location": order.source_location}
#
#         async with self._session.begin():
#             await self._session.execute(text(SAVE_RATING_QUERY_TEMPLATE), params=params)
#
#         return await self.get_by_user_id(order.user_id)
#
#     async def get_by_user_id(self, user_id: str) -> DriveOrder:
#         async with self._session.begin():
#             res = await self._session.execute(select(DriveOrder).where(DriveOrder.user_id == user_id).limit(1))
#         return res.scalar_one_or_none()
#
#     async def get_by_order_id(self, order_id: int) -> DriveOrder:
#         async with self._session.begin():
#             res = await self._session.execute(select(DriveOrder).where(DriveOrder.id == order_id).limit(1))
#         return res.scalar_one_or_none()
#
#     async def delete(self, drive: DriveOrder) -> None:
#         async with self._session.begin():
#             await self._session.delete(drive)
