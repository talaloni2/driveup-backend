from http import HTTPStatus
from typing import TypeVar, Generic, Optional, Coroutine, Any, Type, Union
from httpx import AsyncClient, Response
from pydantic.generics import GenericModel

from model.base_dto import BaseModel

T = TypeVar('T', bound=BaseModel)
_RESP = Union[T, bytes]


class TestClient:
    def __init__(self, client: AsyncClient):
        self._client = client

    async def post(self, url: str, req_body: Optional[BaseModel] = None, resp_model: Optional[Type[T]] = None, assert_status: Optional[int] = HTTPStatus.OK, *args, **kwargs,) -> _RESP:
        if req_body:
            req_body = req_body.dict()
        return await self._execute(self._client.post(url, json=req_body, *args, **kwargs), resp_model, assert_status)

    async def get(self, url: str, resp_model: Type[T] = None, assert_status: Optional[int] = HTTPStatus.OK, *args, **kwargs,) -> _RESP:
        return await self._execute(self._client.get(url, *args, **kwargs), resp_model, assert_status)

    async def delete(self, url: str, resp_model: Optional[Type[T]] = None, assert_status: Optional[int] = HTTPStatus.OK, *args, **kwargs,) -> _RESP:
        return await self._execute(self._client.delete(url, *args, **kwargs), resp_model, assert_status)

    async def _execute(self, coro: Coroutine[Any, Any, Response], resp_model: Optional[Type[T]], assert_status: Optional[int]) -> _RESP:
        resp = await coro
        if assert_status:
            assert resp.status_code == assert_status, resp.text
        if resp_model:
            return resp_model(**resp.json())

        return resp.content

