import random
from uuid import uuid4


def get_random_string() -> str:
    return str(uuid4())


def get_random_email() -> str:
    return f"test_user_{get_random_string()}@gmail.com"


def random_latitude(lower_bound: float = 32.079611, upper_bound: float = 32.068363) -> float:
    return random.uniform(lower_bound, upper_bound)


def random_longitude(lower_bound: float = 34.833261, upper_bound: float = 34.803012) -> float:
    return random.uniform(lower_bound, upper_bound)
