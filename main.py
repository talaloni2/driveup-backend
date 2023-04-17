import uvicorn

import server
from component_factory import get_config

if __name__ == "__main__":
    uvicorn.run(app=server.app, host="0.0.0.0", port=get_config().server_port)
