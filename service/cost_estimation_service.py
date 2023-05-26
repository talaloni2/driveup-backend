from datetime import datetime

from model.configuration import CostEstimationConfig, Tariff
from model.responses.directions_api import DirectionsApiResponse


class CostEstimationService:
    def __init__(self, cost_estimation_config: CostEstimationConfig = None):
        self._cost_estimation_config = cost_estimation_config or CostEstimationConfig()

    def estimate_cost(self, reservation_date: datetime, directions: DirectionsApiResponse):
        return round(self._get_raw_estimation(reservation_date, directions) * self._get_discount_factor(), 2)

    def _get_raw_estimation(self, reservation_date: datetime, directions: DirectionsApiResponse):
        for tariff_class, tariff_times in self._cost_estimation_config.tariff_times_mapping.items():
            for tariff_time in tariff_times:
                if tariff_time.contains(reservation_date):
                    return self._calculate_fare(
                        directions, self._cost_estimation_config.tariff_rates_mapping[tariff_class]
                    )

    def _get_discount_factor(self) -> float:
        return round((100 - self._cost_estimation_config.discount_percent) / 100.0, 2)

    def _calculate_fare(self, directions: DirectionsApiResponse, tariff: Tariff) -> float:
        distance_km = directions.distance_meters / 1000
        time_minutes = directions.duration_seconds / 60
        base_fare = self._cost_estimation_config.base_fare + self._cost_estimation_config.reservation_fare
        return round(base_fare + round(distance_km * tariff.km, 2) + round(time_minutes * tariff.minute, 2), 2)
