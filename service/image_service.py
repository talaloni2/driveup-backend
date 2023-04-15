from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import query

from model.image import Image
from service.db_service import DatabaseService


class ImageService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert_image(self, image: Image) -> Image:
        async with self._session.begin():
            self._session.add(image)

        await self._session.refresh(image)
        return image

    async def get_image(self, id: int) -> Optional[Image]:
        async with self._session.begin():
            res = await self._session.execute(select(Image).where(Image.id == id).limit(1))
        return res.scalar_one_or_none()

    async def delete_image(self, image: Image) -> None:
        async with self._session.begin():
            await self._session.delete(image)
