from old.exceptions import ServerNameTakenException, ExceedMaxServerCountException, VersionException
from old.naming import get_jar_name
from bs4 import BeautifulSoup
import aiohttp
import logging
import os
import re
import shutil
import subprocess
import wget

# configure logger
logger = logging.getLogger("py-server")


class ServerMaker:
    def __init__(self, save_location: str, max_servers: int = 5):
        """
        A server creation object that has a save location and can make servers.
        :param save_location: The base location for servers to be saved at.
        """
        self.server_location = os.path.abspath(save_location)
        os.makedirs(self.server_location, exist_ok=True)
        self.max_servers = max_servers
        if self.max_servers < 0:
            self.max_servers = abs(self.max_servers)
        elif self.max_servers == 0:
            self.max_servers = None
        logger.debug(self.__repr__())

    def get_number_of_servers(self) -> int:
        """ Get the number of servers already saved to this location. """
        return len(os.listdir(self.server_location))

    async def make_server(self, server_name: str, server_version: str = None, overwrite=False):
        """
        Creates a server from where the ServerMaker is operating (save_location).
        :param server_name: Name for the server/file.
        :param server_version: Specified version in format #.#.# if left blank will default to most up to date version.
        :param overwrite: If true will replace a server of the same name, otherwise will throw an error for duplicate names.
        """
        if not self.max_servers or self.max_servers > self.get_number_of_servers() or (
                any([server_name.lower() == file.lower() for file in os.listdir(self.server_location)]) and overwrite):
            server_save_location = os.path.join(self.server_location, server_name)
            logger.debug(f"Creating server {server_save_location}, v={server_version}, o={overwrite}")
            if os.path.exists(server_save_location):
                if overwrite:
                    logger.info(f"Removing {server_save_location} for overwrite")
                    shutil.rmtree(server_save_location)
                else:
                    raise ServerNameTakenException()
            os.makedirs(server_save_location, exist_ok=True)

            if not server_version:
                server_version = await self.get_current_minecraft_version()

            await self.download_jar(
                os.path.join(self.server_location, server_name, get_jar_name(server_version)),
                server_version)
            subprocess.run(f"java -Xms1G -Xmx1G -jar {get_jar_name(server_version)}",
                           stdout=subprocess.DEVNULL, cwd=server_save_location)
            eula_lines = open(os.path.join(server_save_location, "eula.txt"), "r").readlines()[:2] + ["eula=true\n"]
            open(os.path.join(server_save_location, "eula.txt"), "w").writelines(eula_lines)
            logger.debug(f"Eula accepted for server {server_name}")
        else:
            raise ExceedMaxServerCountException()

    @staticmethod
    async def fetch_html(url: str, session: aiohttp.ClientSession, **kwargs) -> str:
        """GET Request wrapper to fetch page html"""
        response = await session.request(method="GET", url=url, **kwargs)
        response.raise_for_status()
        logger.info(f"Got response {response.status} for {url}")
        # await session.close()
        text = await response.text()
        return text

    @staticmethod
    async def get_current_minecraft_version() -> str:
        """Retrieves the current minecraft version from minecraft.net"""
        response = await ServerMaker.fetch_html(r"https://www.minecraft.net/en-us/download/server",
                                                aiohttp.ClientSession())
        return re.search(r"minecraft_server.(?P<version>(.\d*)*).jar",
                         BeautifulSoup(response, "html.parser").find("div", {"class": "minecraft-version"}).find(
                             "a").text).group("version")

    @staticmethod
    async def download_jar(jar_save_location: str, jar_version: str):
        """Download a jar file from mcversions.net to a location"""
        response = await ServerMaker.fetch_html(url=f"https://mcversions.net/download/{jar_version}",
                                                session=aiohttp.ClientSession())
        try:
            download_link = [link for link in
                             BeautifulSoup(response,
                                           "html.parser").find("div", {"class": "downloads"}).find_all("a", href=True)
                             if "server" in link["download"]][0]["href"]
        except IndexError:
            raise VersionException()
        logger.debug(f"Downloading server jar from {download_link} to {jar_save_location}")
        wget.download(download_link, jar_save_location)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return f"ServerMaker loc={self.server_location}, max={self.max_servers}"
