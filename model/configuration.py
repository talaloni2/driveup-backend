from typing import NamedTuple


class Config(NamedTuple):
    server_port: int

    db_host: str
    db_port: int
    db_user: str
    db_pass: str

    knapsack_service_url: str
