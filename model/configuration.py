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
