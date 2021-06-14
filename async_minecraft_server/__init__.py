from async_minecraft_server.server_loader import ServerLoader
from async_minecraft_server.server_maker import ServerMaker
from async_minecraft_server.exceptions import *

import coloredlogs
import logging
import sys

# configure logger
coloredlogs.install(level=logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("py-server")
