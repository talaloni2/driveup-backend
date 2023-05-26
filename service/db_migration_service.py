from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection

from logger import logger
from model.base_db import Base


class DatabaseMigrationService:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def migrate(self):
        try:
            async with self._engine.begin() as conn:
                conn: AsyncConnection
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.error("Got unexpected exception while migrating database.", e)