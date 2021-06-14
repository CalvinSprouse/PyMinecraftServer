from py_minecraft_server.minecraft_server.exceptions import *
from py_minecraft_server.minecraft_server.context_manager import cd
from bs4 import BeautifulSoup
import os
import re
import requests
import shutil
import subprocess
import wget


class ServerMaker:
    def __init__(self, server_location: str, jar_version=None, overwrite=False):
        # define location and create it if it doesn't exist
        self.server_location = os.path.abspath(server_location)
        if overwrite and os.path.exists(self.server_location):
            shutil.rmtree(self.server_location)
        if not os.path.exists(server_location):
            os.makedirs(self.server_location, exist_ok=True)
            self.jar_version = jar_version
            if not jar_version:
                self.jar_version = self.get_current_minecraft_version()
            self.jar_name = f"minecraft_server.{self.jar_version}.jar"
        else:
            raise ServerAlreadyExistsException(server_location)

    def make_server(self):
        self.download_jar(self.server_location, self.jar_name, self.jar_version)
        with cd(self.server_location):
            subprocess.run(f"java -Xms1G -Xmx1G -jar {self.jar_name}")
            eula_lines = open("eula.txt", "r").readlines()[:2] + ["eula=true\n"]
            open("eula.txt", "w").writelines(eula_lines)
        return self

    def get_number_of_servers(self):
        """
        :return: The number of servers adjacent to the current server
        """
        return os.listdir(os.path.basename(self.server_location))

    def get_server_location(self):
        return self.server_location

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def download_jar(jar_save_location: str, jar_save_name: str, jar_version: str):
        """
        Goes to the depth of the web to expose my computer to virus'.
        """
        try:
            download_link = [link for link in
                             BeautifulSoup(requests.get(f"https://mcversions.net/download/{jar_version}").content,
                                           "html.parser").find_all("a", href=True)
                             if "server" in link["href"] and "mojang" in link["href"]][0]
            wget.download(download_link["href"], os.path.join(jar_save_location, jar_save_name))
        except IndexError:
            raise VersionException(jar_version)

    @staticmethod
    def get_current_minecraft_version():
        return re.search(r"minecraft_server.(?P<version>(.\d*)*).jar",
                         BeautifulSoup(requests.get(r"https://www.minecraft.net/en-us/download/server").content,
                                       "html.parser").find("div", {"class": "minecraft-version"}).
                         find("a").text, re.IGNORECASE).group("version")
