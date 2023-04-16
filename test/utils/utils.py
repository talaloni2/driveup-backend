from uuid import uuid4


def get_random_string() -> str:
    return str(uuid4())


def get_random_email() -> str:
    return f"{get_random_string()}@gmail.com"
