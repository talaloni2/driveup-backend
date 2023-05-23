from mappings.factory_mapping import LIMITS_MAPPING
from mappings.utils import limit_by_range
from model.requests.driver import LimitValues, Limit


def test_limit_by_range():
    assert limit_by_range(5, LimitValues(min=1, max=6)) is True
    assert limit_by_range(6, LimitValues(min=1, max=6)) is True
    assert limit_by_range(1, LimitValues(min=1, max=6)) is True
    assert limit_by_range(7, LimitValues(min=1, max=6)) is False
    assert limit_by_range(0, LimitValues(min=1, max=6)) is False


def test_limit_mapping():
    class Order:
        def __init__(self, distance_from_driver, distance):
            self.distance_from_driver = distance_from_driver
            self.distance = distance

    assert LIMITS_MAPPING[Limit.pick_up_distance.value](
        order=Order(distance_from_driver=5, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.pick_up_distance.value](
        order=Order(distance_from_driver=1, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.pick_up_distance.value](
        order=Order(distance_from_driver=6, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.pick_up_distance.value](
        order=Order(distance_from_driver=0, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is False
    assert LIMITS_MAPPING[Limit.pick_up_distance.value](
        order=Order(distance_from_driver=7, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is False
    assert LIMITS_MAPPING[Limit.ride_distance.value](
        order=Order(distance_from_driver=0, distance=5),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.ride_distance.value](
        order=Order(distance_from_driver=0, distance=1),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.ride_distance.value](
        order=Order(distance_from_driver=0, distance=6),
        limit_values=LimitValues(min=1, max=6)
    ) is True
    assert LIMITS_MAPPING[Limit.ride_distance.value](
        order=Order(distance_from_driver=0, distance=0),
        limit_values=LimitValues(min=1, max=6)
    ) is False
    assert LIMITS_MAPPING[Limit.ride_distance.value](
        order=Order(distance_from_driver=0, distance=7),
        limit_values=LimitValues(min=1, max=6)
    ) is False
