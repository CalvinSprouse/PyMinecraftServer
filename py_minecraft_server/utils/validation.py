from py_minecraft_server import logger
import py_minecraft_server.utils
import re


def validate_version(version: str, is_forge: bool = False) -> str:
    """Checks to ensure the version is a valid minecraft version"""
    version_search = re.search(r"^([.]?(?P<version>([.]?\d+)+))", version.strip(), re.IGNORECASE)
    if version_search:
        version = version_search.group("version")
        if is_forge:
            if py_minecraft_server.utils.simple_request(
                    py_minecraft_server.utils.get_forge_url(version), ignore_errors=True).status_code == 200:
                logger.debug(f"Validated forge version {version}")
                return version
        else:
            if len(py_minecraft_server.utils.soupify_url(py_minecraft_server.utils.get_vanilla_url(version),
                                                         ignore_errors=True).find_all(
                    "div", {"class": "error-template"})) == 0:
                logger.debug(f"Validated vanilla version {version}")
                return version
    raise ValueError(f"Version does not exist {version} is_forge={is_forge}")
