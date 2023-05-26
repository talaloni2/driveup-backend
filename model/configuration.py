from dataclasses import dataclass
from datetime import time, datetime
from enum import Enum
from typing import NamedTuple, Optional


class Config(NamedTuple):
    server_port: int

    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_url: Optional[str]
    users_handler_base_url: str
    subscriptions_handler_base_url: str

    knapsack_service_url: str

    geocoding_api_key: str
    directions_api_key: str


class TimeRange(NamedTuple):
    day: int  # Sunday: 6, Monday: 0, Tuesday: 1, Wednesday: 2, Thursday: 3, Friday: 4, Saturday: 5
    start: time
    end: time

    def contains(self, dt: datetime):
        return dt.weekday() == self.day and self.start <= dt.time() < self.end


class TariffClass(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class Tariff(NamedTuple):
    km: float
    minute: float


@dataclass
class CostEstimationConfig:
    nis_to_usd_rate: float = 0.27
    base_fare: float = 11.85
    reservation_fare: float = 5.47
    minute_tariff_a: float = 1.86
    km_tariff_a: float = 1.86
    minute_tariff_b: float = 2.22
    km_tariff_b: float = 2.22
    minute_tariff_c: float = 2.6
    km_tariff_c: float = 2.6

    discount_percent: int = 20

    def __post_init__(self):
        self.tariff_rates_mapping: dict[TariffClass, Tariff] = {
            TariffClass.A: Tariff(1.86, 1.86),
            TariffClass.B: Tariff(2.22, 2.22),
            TariffClass.C: Tariff(2.6, 2.6),
        }

        tariff_a_times: list[TimeRange] = [TimeRange(a, time(6), time(21)) for a in (6, 0, 1, 2, 3)] + [
            TimeRange(4, time(6), time(16))
        ]
        tariff_b_times: list[TimeRange] = (
            [TimeRange(a, time(21, 1), time.max) for a in (6, 0, 1, 2)]
            + [TimeRange(a, time(), time(6)) for a in (0, 1, 2, 3)]
            + [TimeRange(3, time(21), time(23))]
            + [TimeRange(4, time(16), time(21))]
            + [TimeRange(5, time(6), time(19))]
        )
        tariff_c_times: list[TimeRange] = [
            TimeRange(3, time(23), time.max),
            TimeRange(4, time(0), time(6)),
            TimeRange(4, time(21), time.max),
            TimeRange(5, time(0), time(6)),
            TimeRange(5, time(19), time.max),
            TimeRange(6, time(0), time(6)),
        ]

        self.tariff_times_mapping: dict[TariffClass, list[TimeRange]] = {
            TariffClass.A: tariff_a_times,
            TariffClass.B: tariff_b_times,
            TariffClass.C: tariff_c_times,
        }
