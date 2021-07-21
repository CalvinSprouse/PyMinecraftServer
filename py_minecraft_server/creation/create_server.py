from py_minecraft_server import logger
from py_minecraft_server.utils import validate_version
import py_minecraft_server.creation
import asyncio
import os


# TODO: Put java ref finder in utils
async def create_server(server_location: str, server_version: str, jar_save_location: str = None,
                        is_forge: bool = False, java_ref: str = "java"):
    server_version = validate_version(server_version, is_forge)
    if os.path.isdir(server_location):
        raise ValueError(f"{server_location} already exists")
    os.makedirs(server_location)
    logger.debug(f"Created server dir @{server_location}")
    if jar_save_location:
        await py_minecraft_server.creation.download_jar(server_version, jar_save_location, is_forge,
                                                        False, False, "java", *[server_location])
    else:
        await py_minecraft_server.creation.download_jar(server_version, server_location, is_forge)
    # Call the server and preform inits
    # TODO: Move batch creator to creation

