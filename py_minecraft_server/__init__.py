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

# TODO: Normalize Exceptions between async/def versions
# TODO: Re-write def with new knowledge/remove loaders ref to maker
