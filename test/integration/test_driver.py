import pytest

from model.requests.driver import DriverRequestDrive
from test.utils.test_client import TestClient

pytestmart = pytest.mark.asyncio

EMAIL = "a@b.com"
PASSENGER_AMOUNT = 1
CURRENT_LAT = 1
CURRENT_LON = 1
ORDER_ID = 1


async def test_post_request_drive(test_client: TestClient, ensure_db_schema: None):
    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
        limits={},
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert 'time' in resp_json
    assert 'solutions' in resp_json


async def test_accept_drive(test_client: TestClient, ensure_db_schema: None):
    request_drive_request = DriverRequestDrive(
        current_lat=CURRENT_LAT,
        current_lon=CURRENT_LON,
    )
    resp = await test_client.post(
        url="/driver/request-drives",
        req_body=request_drive_request,
    )
    assert resp.status_code == 200





