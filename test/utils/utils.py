import random
from uuid import uuid4


def get_random_string() -> str:
    return str(uuid4())


def get_random_email() -> str:
    return f"test_user_{get_random_string()}@gmail.com"


def random_latitude(around: float = 32.069188, radius: float = 1) -> float:
    return random.uniform(around - radius, around + radius)


def random_longitude(around: float = 34.805322, radius: float = 1) -> float:
    return random.uniform(around - radius, around + radius)
