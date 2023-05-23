from mappings.utils import limit_by_range
from model.requests.driver import Limit

LIMITS_MAPPING = {
    Limit.pick_up_distance.value: lambda order, limit_values: limit_by_range(order.distance_from_driver, limit_values),
    Limit.ride_distance.value: lambda order, limit_values: limit_by_range(order.distance, limit_values),
}
