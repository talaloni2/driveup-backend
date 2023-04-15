from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection

from model.base_db import Base


class DatabaseMigrationService:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def migrate(self):
        async with self._engine.begin() as conn:
            conn: AsyncConnection
            await conn.run_sync(Base.metadata.create_all)
