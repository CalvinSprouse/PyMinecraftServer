import coloredlogs
import logging

logger = logging.getLogger("py-minecraft-server")
coloredlogs.install(logging.DEBUG, logger=logger)
