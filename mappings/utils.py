from typing import Any

from model.requests.driver import LimitValues


def limit_by_range(value: Any, limit_values: LimitValues) -> bool:
    if limit_values.min and value < limit_values.min:
        return False
    if limit_values.max and value > limit_values.max:
        return False
    return True
