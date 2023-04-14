from sqlalchemy.ext.asyncio import AsyncSession

from model.image import Image


class ImageService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert_image(self, image: Image):
        async with self._session.begin():
            self._session.add(image)
        await self._session.refresh(image)
