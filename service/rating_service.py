import textwrap

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.user_rating import UserRating, USER_RATING_TABLE

SAVE_RATING_QUERY_TEMPLATE = textwrap.dedent(
    f"""
INSERT INTO {USER_RATING_TABLE} (email, rating, raters_count)
VALUES (:email, :rating, 1)
ON CONFLICT (email) DO UPDATE
SET 
email = EXCLUDED.email, 
rating = (EXCLUDED.rating * EXCLUDED.raters_count + {USER_RATING_TABLE}.rating * {USER_RATING_TABLE}.raters_count) / (EXCLUDED.raters_count + {USER_RATING_TABLE}.raters_count),
raters_count = {USER_RATING_TABLE}.raters_count + 1;
"""
)


class RatingService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, rating: UserRating) -> UserRating:
        params = {"email": rating.email, "rating": rating.rating}
        # async with self._session.begin():
        await self._session.execute(text(SAVE_RATING_QUERY_TEMPLATE), params=params)

        return await self.get_by_email(rating.email)

    async def get_by_email(self, email: str) -> UserRating:
        # async with self._session.begin():
        res = await self._session.execute(select(UserRating).where(UserRating.email == email).limit(1))
        return res.scalar_one_or_none()

    async def delete(self, rating: UserRating) -> None:
        # async with self._session.begin():
        await self._session.delete(rating)
