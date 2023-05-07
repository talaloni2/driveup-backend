from typing import Optional

from fastapi import HTTPException
from httpx import AsyncClient

from model.requests.user import UserHandlerLoginRequest, UserHandlerCreateUserRequest
from model.responses.user import UserHandlerResponse


class UserHandlerService:
    def __init__(self, http_client: AsyncClient):
        self._client: AsyncClient = http_client

    async def login(self, username: str, password: str) -> dict:
        request = UserHandlerLoginRequest(username=username, password=password)
        response = await self._client.post("/token", data=request.dict())
        response.raise_for_status()

        return response.json()

    async def validate_token(self, token: str) -> UserHandlerResponse:
        response = await self._client.get("/users/validate_token", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()

        return UserHandlerResponse(**response.json())

    async def create_user(self, email: str, password: str, phone_number: str, full_name: str, car_model: Optional[str],
                          car_color: Optional[str], plate_number: Optional[str]) -> UserHandlerResponse:
        request = UserHandlerCreateUserRequest(
            email=email,
            password=password,
            phone_number=phone_number,
            full_name=full_name,
            car_model=car_model,
            car_color=car_color,
            plate_number=plate_number
        )
        response = await self._client.post("/users/", json={"parameter": request.dict()})
        if response.status_code == 400:
            raise HTTPException(status_code=400, detail=response.json()["detail"])
        response.raise_for_status()

        return UserHandlerResponse(**response.json())
