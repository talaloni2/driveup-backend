from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class DatabaseService:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker

    class _DatabaseSession:
        def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
            self._session_maker = session_maker

        async def __aenter__(self) -> AsyncSession:
            self._session_ctx = self._session_maker()
            session = await self._session_ctx.__aenter__()

            self._txn_ctx = session.begin()
            await self._txn_ctx.__aenter__()
            return session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self._session_ctx.__aexit__(exc_type, exc_val, exc_tb)
            await self._txn_ctx.__aexit__(exc_type, exc_val, exc_tb)

    def _begin_session(self) -> _DatabaseSession:
        return self._DatabaseSession(self._session_maker)
