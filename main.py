import asyncio

import uvicorn

import server
from component_factory import get_config
from model.configuration import Config


def main(config: Config):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


if __name__ == "__main__":
    main(get_config())
