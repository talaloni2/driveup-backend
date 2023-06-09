import os
from functools import lru_cache

from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from model.configuration import Config, CostEstimationConfig
from service.cost_estimation_service import CostEstimationService
from service.db_migration_service import DatabaseMigrationService
from service.directions_service import DirectionsService
from service.driver_service import DriverService
from service.geocoding_service import GeocodingService
from service.image_normalization_service import ImageNormalizationService
from service.image_service import ImageService
from service.knapsack_service import KnapsackService
from service.rating_service import RatingService
from service.passenger_service import PassengerService
from service.subscription_handler_service import SubscriptionHandlerService
from service.time_service import TimeService
from service.user_handler_service import UserHandlerService


def get_config() -> Config:
    return Config(
        server_port=int(os.getenv("SERVER_PORT", "8000")),
        db_user=os.getenv("DB_USER"),
        db_pass=os.getenv("DB_PASS"),
        db_host=os.getenv("DB_HOST"),
        db_port=int(os.getenv("DB_PORT", "0")),
        knapsack_service_url=os.getenv("KNAPSACK_SERVICE_URL", "http://localhost:8001"),
        db_url=os.getenv("DB_URL"),
        users_handler_base_url=os.getenv("USERS_HANDLER_BASE_URL"),
        subscriptions_handler_base_url=os.getenv("SUBSCRIPTIONS_HANDLER_BASE_URL"),
        geocoding_api_key=os.getenv("GEOCODING_API_KEY"),
        directions_api_url=os.getenv("DIRECTIONS_API_URL"),
    )


def get_database_url(config: Config = Depends(get_config)) -> str:
    return (
        config.db_url
        if config.db_url is not None
        else f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/drive_up"
    )


@lru_cache()
def create_db_engine(db_url: str = Depends(get_database_url)) -> AsyncEngine:
    return create_async_engine(
        db_url,
        future=True,
        poolclass=NullPool,
    )

    # return eng.execution_options(isolation_level="AUTOCOMMIT")


@lru_cache()
def get_db_session_maker(engine: AsyncEngine = Depends(create_db_engine)) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_db_session_maker),
) -> AsyncSession:
    async with session_maker() as session:
        async with session.begin():
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


def get_passenger_service(db_session: AsyncSession = Depends(get_db_session)):
    return PassengerService(db_session)


def get_driver_service(db_session: AsyncSession = Depends(get_db_session), passenger_service: PassengerService = Depends(get_passenger_service)):
    return DriverService(db_session, passenger_service)


def get_user_handler_service(config: Config = Depends(get_config)):
    client = AsyncClient(base_url=config.users_handler_base_url)
    return UserHandlerService(client)


def get_subscription_handler_service(config: Config = Depends(get_config)):
    client = AsyncClient(base_url=config.subscriptions_handler_base_url)
    return SubscriptionHandlerService(client)


def get_time_service() -> TimeService:
    return TimeService()


def get_knapsack_service(config: Config = Depends(get_config), time_service: TimeService = Depends(get_time_service)):
    client = AsyncClient(base_url=config.knapsack_service_url)
    return KnapsackService(client, time_service)


def get_geocoding_service(config: Config = Depends(get_config)):
    client = AsyncClient(base_url="https://geocode.search.hereapi.com/v1")
    return GeocodingService(client, config.geocoding_api_key)


def get_directions_service(config: Config = Depends(get_config)) -> DirectionsService:
    return DirectionsService(config.directions_api_url, http_client=AsyncClient(base_url=config.knapsack_service_url))


def get_cost_estimation_config() -> CostEstimationConfig:
    return CostEstimationConfig()


def get_cost_estimation_service(
    config: CostEstimationConfig = Depends(get_cost_estimation_config),
) -> CostEstimationService:
    return CostEstimationService(config)
