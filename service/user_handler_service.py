from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from httpx import AsyncClient

from model.requests.user import UserHandlerLoginRequest, UserHandlerCreateUserRequest, UserHandlerUpdateUserRequest
from model.responses.user import UserHandlerResponse, UserHandlerGetByEmailResponse


class UserHandlerService:
    def __init__(self, http_client: AsyncClient):
        self._client: AsyncClient = http_client

    async def login(self, username: str, password: str) -> Optional[dict]:
        request = UserHandlerLoginRequest(username=username, password=password)
        response = await self._client.post("/users/token", data=request.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        return response.json()

    async def validate_token(self, token: str) -> UserHandlerResponse:
        response = await self._client.get("/users/validate_token", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token invalid or expired")
        response.raise_for_status()

        return UserHandlerResponse(**response.json())

    async def get_users(self, token: str) -> UserHandlerResponse:
        response = await self._client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()

        return UserHandlerResponse(**response.json())

    async def get_user_by_email(self, email: str, token: str) -> UserHandlerGetByEmailResponse:
        response = await self._client.get(f"/users/{email}", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()

        return UserHandlerGetByEmailResponse(**response.json())

    async def update_user(self, email: str, token: str, full_name: Optional[str], car_model: Optional[str],
                          car_color: Optional[str], plate_number: Optional[str], **kwargs) -> UserHandlerResponse:
        request = UserHandlerUpdateUserRequest(
            full_name=full_name,
            car_model=car_model,
            car_color=car_color,
            plate_number=plate_number
        )
        response = await self._client.put(f"/users/{email}", json={"parameter": request.dict()}, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()

        return UserHandlerResponse(**response.json())

    async def delete_user(self, email: str, token: str) -> UserHandlerResponse:
        response = await self._client.delete(f"/users/{email}", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()

        return UserHandlerResponse(**response.json())

    async def create_user(
        self,
        email: str,
        password: str,
        phone_number: str,
        full_name: str,
        car_model: Optional[str],
        car_color: Optional[str],
        plate_number: Optional[str],
    ) -> UserHandlerResponse:
        request = UserHandlerCreateUserRequest(
            email=email,
            password=password,
            phone_number=phone_number,
            full_name=full_name,
            car_model=car_model,
            car_color=car_color,
            plate_number=plate_number,
        )
        response = await self._client.post("/users/", json={"parameter": request.dict()})
        if response.status_code == 400:
            raise HTTPException(status_code=400, detail=response.json()["detail"])
        response.raise_for_status()

        return UserHandlerResponse(**response.json())
