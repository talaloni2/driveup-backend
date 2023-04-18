import pytest

from component_factory import get_rating_service, get_db_session_maker, create_db_engine, get_database_url, get_config
from model.user_rating import UserRating
from service.rating_service import RatingService
from test.utils.utils import get_random_email

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def rating_service() -> RatingService:
    async with get_db_session_maker(create_db_engine(get_database_url(get_config())))() as session:
        yield get_rating_service(session)


async def test_get_rating(rating_service: RatingService, ensure_db_schema: None):
    email = get_random_email()
    rating = UserRating(email=email, rating=2, raters_count=1)
    await rating_service.save(rating)
    result_rating = await rating_service.get_by_email(email)

    assert result_rating is not None
    assert result_rating.rating == rating.rating
    assert result_rating.raters_count == rating.raters_count
    assert result_rating.email == rating.email


async def test_save_rating(rating_service: RatingService, ensure_db_schema: None):
    email = get_random_email()
    await rating_service.save(UserRating(email=email, rating=4, raters_count=1))
    await rating_service.save(UserRating(email=email, rating=3, raters_count=1))
    final_rating = await rating_service.save(UserRating(email=email, rating=2, raters_count=1))

    assert final_rating.rating == 3
    assert final_rating.raters_count == 3
    assert final_rating.email == email


async def test_delete_rating(rating_service: RatingService, ensure_db_schema: None):
    email = get_random_email()
    rating = await rating_service.save(UserRating(email=email, rating=4, raters_count=1))
    existing = await rating_service.get_by_email(email)
    await rating_service.delete(rating)
    not_existing = await rating_service.get_by_email(email)

    assert existing
    assert not not_existing
