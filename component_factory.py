import os
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import PoolProxiedConnection, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from model.configuration import Config
from service.db_migration_service import DatabaseMigrationService
from service.image_normalization_service import ImageNormalizationService
from service.image_service import ImageService


def get_config() -> Config:
    return Config(
        server_port=int(os.getenv("SERVER_PORT", "8000")),
        db_user=os.environ["DB_USER"],
        db_pass=os.environ["DB_PASS"],
        db_host=os.environ["DB_HOST"],
        db_port=int(os.environ["DB_PORT"]),
    )


def get_database_url(config: Config = Depends(get_config)) -> str:
    return f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/postgres"


@lru_cache()
def _create_db_engine(db_url: str = Depends(get_database_url)) -> AsyncEngine:
    return create_async_engine(db_url, future=True)


@lru_cache()
def get_db_session_maker(engine: AsyncEngine = Depends(_create_db_engine)) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session(session_maker: async_sessionmaker[AsyncSession] = Depends(get_db_session_maker)) \
        -> AsyncSession:
    async with session_maker() as session:
        yield session


def get_image_service(db_session: AsyncSession = Depends(get_db_session)):
    return ImageService(db_session)


def get_migration_service(db_engine: AsyncEngine = _create_db_engine(get_database_url(get_config()))):
    return DatabaseMigrationService(db_engine)


def get_image_normalization_service():
    return ImageNormalizationService()
