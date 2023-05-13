from httpx import AsyncClient

from model.responses.subscription import SubscriptionHandlerResponse


class SubscriptionHandlerService:
    def __init__(self, http_client: AsyncClient):
        self._client: AsyncClient = http_client

    async def get_by_user_email(self, email: str) -> SubscriptionHandlerResponse:
        response = await self._client.get(f"/users_map/{email}")

        return SubscriptionHandlerResponse(**response.json())
