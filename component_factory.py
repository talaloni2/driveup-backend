import os
from functools import lru_cache

from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy import PoolProxiedConnection, MetaData, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from model.configuration import Config
from service.db_migration_service import DatabaseMigrationService
from service.image_normalization_service import ImageNormalizationService
from service.image_service import ImageService
from service.knapsack_service import KnapsackService
from service.rating_service import RatingService


def get_config() -> Config:
    return Config(
        server_port=int(os.getenv("SERVER_PORT", "8000")),
        db_user=os.environ["DB_USER"],
        db_pass=os.environ["DB_PASS"],
        db_host=os.environ["DB_HOST"],
        db_port=int(os.environ["DB_PORT"]),
        knapsack_service_url=os.getenv("KNAPSACK_SERVICE_URL", "http://localhost:8001"),
        db_url=os.environ["DB_URL"] if "DB_URL" in os.environ else None,
        users_handler_base_url=os.environ["USERS_HANDLER_BASE_URL"],
        subscriptions_handler_base_url=os.environ["SUBSCRIPTIONS_HANDLER_BASE_URL"],
    )


def get_database_url(config: Config = Depends(get_config)) -> str:
    return config.db_url if config.db_url is not None else f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/postgres"


@lru_cache()
def create_db_engine(db_url: str = Depends(get_database_url)) -> AsyncEngine:
    return create_async_engine(
        db_url,
        future=True,
        poolclass=NullPool,
    )


@lru_cache()
def get_db_session_maker(engine: AsyncEngine = Depends(create_db_engine)) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session(
        session_maker: async_sessionmaker[AsyncSession] = Depends(get_db_session_maker),
) -> AsyncSession:
    async with session_maker() as session:
        yield session


def get_image_service(db_session: AsyncSession = Depends(get_db_session)):
    return ImageService(db_session)


def get_migration_service(db_engine: AsyncEngine = None):
    db_engine = db_engine or create_db_engine(get_database_url(get_config()))
    return DatabaseMigrationService(db_engine)


def get_image_normalization_service():
    return ImageNormalizationService()


def get_rating_service(db_session: AsyncSession = Depends(get_db_session)):
    return RatingService(db_session)


def get_knapsack_service(config: Config = Depends(get_config)):
    client = AsyncClient(base_url=config.knapsack_service_url)
    return KnapsackService(client)
