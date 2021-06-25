# TODO: Fix imports
from py_minecraft_server.utils import validate_version, soupify_url, get_vanilla_url, get_forge_url
from py_minecraft_server.logging import logger
import asyncio
import threading
import time
import urllib.request
import os
import shutil


# TODO: Consider converting to hostingfiles.lol
async def download_jar(version: str, save_location: str, is_forge: bool, create_dirs: bool = False,
                       overwrite: bool = False, *copy_locations):
    """
    Downloads a jar to the desired location
    :param version: The version of minecraft to get a server jar for
    :param save_location: The location to save the jar too
    :param is_forge: True if the jar is meant to be a forge jar
    :param create_dirs: Weather or not to make the directory if it doesnt exist
    :param overwrite: Delete a file in save_location if present
    :param copy_locations: Additional locations to copy the downloaded file to, create_dirs will apply to copy_locations
    """
    # validate version and save location
    version = validate_version(version)
    if not save_location.endswith(".jar"):
        raise ValueError(f"Illegal save location, must be a .jar file: {save_location}")
    if os.path.exists(save_location):
        if not overwrite:
            raise ValueError(f"Illegal save location, must be empty: {save_location}")
        logger.warning(f"Deleting file @{os.path.abspath(save_location)} because overwrite={overwrite}")
        os.remove(save_location)
    if create_dirs:
        os.makedirs(os.path.dirname(save_location), exist_ok=True)

    if is_forge:
        try:
            download_url = soupify_url(get_forge_url(version)).find(
                "div", {"class": "link-boosted"}).find("a").get("href").split("url=")[1]
        except AttributeError:
            raise ValueError(f"Illegal forge version, no forge download for version {version}")
    else:
        download_url = soupify_url(get_vanilla_url(version)).find(
            "a", {"download": f"minecraft_server-{version}.jar"}).get("href")
    logger.debug(f"Async download started from {download_url} to {save_location}")
    await thread_download(download_url, save_location)
    if copy_locations:
        for location in copy_locations:
            copy_file(save_location, location)


async def thread_download(url: str, save_location: str):
    """Threads a download from urllib.request.urlretreive"""
    t = threading.Thread(target=urllib.request.urlretrieve, args=(url, save_location), daemon=True)
    t.start()
    start_time = time.time()
    while t.is_alive():
        await asyncio.sleep(1)
    logger.debug(f"Download from {url} to {save_location} completed in {(time.time() - start_time):.2f}s")


def copy_file(src: str, dst: str, create_dirs: bool = False):
    """Copy a file from src to dst allowing for dirs to be created"""
    if create_dirs:
        os.makedirs(os.path.basename(dst), exist_ok=True)
    if os.path.exists(dst):
        raise ValueError(f"Destination not empty {dst}")
    if not os.path.isfile(src):
        raise ValueError(f"Source is not a file {src}")
    logger.debug(f"Copying {src} to {dst}")
    shutil.copy2(src, dst)
