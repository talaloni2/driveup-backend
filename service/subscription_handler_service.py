from httpx import AsyncClient

from model.requests.subscription import SubscriptionHandlerCreateUserSubscriptionMapRequest
from model.responses.subscription import SubscriptionHandlerResponse


class SubscriptionHandlerService:
    def __init__(self, http_client: AsyncClient):
        self._client: AsyncClient = http_client

    async def get_by_user_email(self, email: str) -> SubscriptionHandlerResponse:
        response = await self._client.get(f"/users_map/{email}")

        return SubscriptionHandlerResponse(**{**response.json(), **{"code": response.status_code}})

    async def get_user_subscription_maps(self) -> SubscriptionHandlerResponse:
        response = await self._client.get(f"/user_subscription_maps/")

        return SubscriptionHandlerResponse(**{**response.json(), **{"code": response.status_code}})

    async def get_user_subscription_map(self, email: str, name: str) -> SubscriptionHandlerResponse:
        response = await self._client.get(f"/user_subscription_maps/{email}/{name}")

        return SubscriptionHandlerResponse(**{**response.json(), **{"code": response.status_code}})

    async def delete_user_subscription_map(self, email: str, name: str) -> SubscriptionHandlerResponse:
        response = await self._client.delete(f"/user_subscription_maps/{email}/{name}")

        return SubscriptionHandlerResponse(**{**response.json(), **{"code": response.status_code}})

    async def create_user_subscription_map(
        self, subscription_name: str, user_email: str, card_owner_id: str, card_number: str, cvv: str, **kwargs
    ) -> SubscriptionHandlerResponse:
        request = SubscriptionHandlerCreateUserSubscriptionMapRequest(
            subscription_name=subscription_name,
            user_email=user_email,
            card_owner_id=card_owner_id,
            card_number=card_number,
            cvv=cvv,
        )
        response = await self._client.post(f"/user_subscription_maps/", json={"parameter": request.dict()})

        return SubscriptionHandlerResponse(**{**response.json(), **{"code": response.status_code}})
