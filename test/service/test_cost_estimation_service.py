from datetime import datetime

import pytest

# Refer to https://taxitariff.co.il/
from model.configuration import CostEstimationConfig
from model.responses.directions_api import DirectionsApiResponse
from service.cost_estimation_service import CostEstimationService


@pytest.mark.parametrize(
    "est_minutes, est_km, dt, discount_percent, expected_cost",
    [
        [10, 4, datetime(2023, 5, 14, 10), 0, 43.36],
        [10, 4, datetime(2023, 5, 14, 23), 0, 48.40],
        [10, 4, datetime(2023, 5, 18, 22, 10), 0, 48.40],
        [10, 4, datetime(2023, 5, 18, 23, 10), 0, 53.72],
        [10, 4, datetime(2023, 5, 19, 10), 0, 43.36],
        [10, 4, datetime(2023, 5, 19, 16, 10), 0, 48.40],
        [10, 4, datetime(2023, 5, 19, 21, 10), 0, 53.72],
        [10, 4, datetime(2023, 5, 20, 10), 0, 48.40],
        [10, 4, datetime(2023, 5, 20, 19, 10), 0, 53.72],
        [10, 4, datetime(2023, 5, 21), 0, 53.72],

        [50, 60, datetime(2023, 5, 14, 10), 0, 221.92],
        [50, 60, datetime(2023, 5, 14, 23), 0, 261.52],
        [50, 60, datetime(2023, 5, 18, 22, 10), 0, 261.52],
        [50, 60, datetime(2023, 5, 18, 23, 10), 0, 303.32],
        [50, 60, datetime(2023, 5, 19, 10), 0, 221.92],
        [50, 60, datetime(2023, 5, 19, 16, 10), 0, 261.52],
        [50, 60, datetime(2023, 5, 19, 21, 10), 0, 303.32],
        [50, 60, datetime(2023, 5, 20, 10), 0, 261.52],
        [50, 60, datetime(2023, 5, 20, 19, 10), 0, 303.32],
        [50, 60, datetime(2023, 5, 21), 0, 303.32],
        
        
        [10, 4, datetime(2023, 5, 14, 10), 20, 34.69],
        [10, 4, datetime(2023, 5, 14, 23), 20, 38.72],
        [10, 4, datetime(2023, 5, 18, 22, 10), 20, 38.72],
        [10, 4, datetime(2023, 5, 18, 23, 10), 20, 42.98],
        [10, 4, datetime(2023, 5, 19, 10), 20, 34.69],
        [10, 4, datetime(2023, 5, 19, 16, 10), 20, 38.72],
        [10, 4, datetime(2023, 5, 19, 21, 10), 20, 42.98],
        [10, 4, datetime(2023, 5, 20, 10), 20, 38.72],
        [10, 4, datetime(2023, 5, 20, 19, 10), 20, 42.98],
        [10, 4, datetime(2023, 5, 21), 20, 42.98],

        [50, 60, datetime(2023, 5, 14, 10), 20, 177.54],
        [50, 60, datetime(2023, 5, 14, 23), 20, 209.22],
        [50, 60, datetime(2023, 5, 18, 22, 10), 20, 209.22],
        [50, 60, datetime(2023, 5, 18, 23, 10), 20, 242.66],
        [50, 60, datetime(2023, 5, 19, 10), 20, 177.54],
        [50, 60, datetime(2023, 5, 19, 16, 10), 20, 209.22],
        [50, 60, datetime(2023, 5, 19, 21, 10), 20, 242.66],
        [50, 60, datetime(2023, 5, 20, 10), 20, 209.22],
        [50, 60, datetime(2023, 5, 20, 19, 10), 20, 242.66],
        [50, 60, datetime(2023, 5, 21), 20, 242.66],
    ]
)
def test_cost_estimation_service(est_minutes: float, est_km: float, dt: datetime, discount_percent, expected_cost: float):
    estimation = CostEstimationService(CostEstimationConfig(discount_percent=discount_percent)).estimate_cost(dt, DirectionsApiResponse(distance_meters=est_km * 1000, duration_seconds=est_minutes * 60))
    assert estimation == expected_cost
