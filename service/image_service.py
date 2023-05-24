from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.image import Image


class ImageService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert(self, image: Image) -> Image:
        async with self._session.begin_nested():
            self._session.add(image)

        await self._session.refresh(image)
        return image

    async def get_by_email(self, email: str) -> Optional[Image]:
        # async with self._session.begin():
        res = await self._session.execute(select(Image).where(Image.related_email == email).limit(1))
        return res.scalar_one_or_none()

    async def get(self, id: int) -> Optional[Image]:
        # async with self._session.begin():
        res = await self._session.execute(select(Image).where(Image.id == id).limit(1))
        return res.scalar_one_or_none()

    async def delete(self, image: Image) -> None:
        # async with self._session.begin():
        await self._session.delete(image)
