from py_minecraft_server import logger
from mctools import RCONClient, QUERYClient


# TODO: Check to ensure rcon/query and required settings are set before creating the instance
class ServerRCON(RCONClient):
    """Establishes a server connection with mctools.RCONClient and automatically logs in"""
    def __init__(self, host: str, password: str, port: int = 25575, timeout: int = 60):
        super().__init__(host=host, port=port, timeout=timeout)
        self.login(password)
        if self.is_connected() and self.is_authenticated():
            logger.info(f"Connected to server {host}:{port} with RCON")


class ServerQuery(QUERYClient):
    """Establishes a server connection with mctools.QUERYClient"""
    def __init__(self, host: str, port: int = 25565, timeout: int = 60):
        super().__init__(host=host, port=port, timeout=timeout)
        if self.is_connected():
            logger.info(f"Connected to server {host}:{port} with QUERY")
