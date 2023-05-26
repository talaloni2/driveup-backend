import pytest

from component_factory import get_directions_service, get_config
from logger import logger
from model.responses.geocode import Geocode


@pytest.mark.skip("This test using the actual directions api. Do not skip if there is an issue there")
async def test_directions_api():
    svc = get_directions_service(get_config())
    resp = await svc.get_directions(
        Geocode(longitude=34.806845, latitude=32.078039), Geocode(longitude=34.791873, latitude=32.080134)
    )
    logger.info(f"Duration seconds: {resp.duration_seconds}. Distance meters: {resp.distance_meters}")
    assert resp.duration_seconds > 0
    assert resp.distance_meters > 0
