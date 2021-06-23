import sys

from py_minecraft_server.exceptions import *
from py_minecraft_server import OpenProperties
from bs4 import BeautifulSoup
import coloredlogs
import logging
import os
import re
import requests
import shutil
import subprocess
import wget

SUB_DIRS = ["Servers", "ServerJars", "ServerMods"]


class ServerManager:
    def __init__(self, master_dir: str, logging_handler: logging.Handler = logging.StreamHandler(),
                 logging_level: int = logging.WARNING, java_install_location: str = "C:\\Program Files\\Java"):
        # ensure dir and sub_dirs exists
        self.master_dir = master_dir
        self.server_dir = os.path.join(self.master_dir, "Servers")
        self.deleted_server_dir = os.path.join(self.master_dir, "DeletedServers")
        self.server_jars_dir = os.path.join(self.master_dir, "ServerJars")
        self.server_mods_dir = os.path.join(self.master_dir, "ServerMods")
        for sub_dir in [self.deleted_server_dir, self.server_jars_dir, self.server_mods_dir]:
            os.makedirs(sub_dir, exist_ok=True)

        # establish java calls
        # TODO: Find multi-java install solution
        java8_dir = re.search(r"(?P<dir>jdk[-]?1.8.0_\d*)", "\n".join(os.listdir(java_install_location))).group("dir")
        self.java8 = os.path.join(java_install_location, java8_dir, 'bin', 'java.exe')
        java16_dir = re.search(r"(?P<dir>jdk[-]?16.\d+.\d+)", "\n".join(os.listdir(java_install_location))).group("dir")
        self.java16 = os.path.join(java_install_location, java16_dir, 'bin', 'java.exe')

        # for active servers
        self.active_server = {"process": None, "name": None}

        # configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging_handler)
        self.logger.setLevel(logging_level)
        coloredlogs.install(logging_level, logger=self.logger)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def log(self, level: int, msg: str, *args, **kwargs):
        self.logger.log(level=level, msg=msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self.log(level=logging.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.log(level=logging.INFO, msg=msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.log(level=logging.WARNING, msg=msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.log(level=logging.ERROR, msg=msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.log(level=logging.CRITICAL, msg=msg, *args, **kwargs)

    def move_master_dir(self, new_location: str):
        """Moves the master_dir and all sub_folders"""
        # TODO: Ensure no servers in self.master_dir are running
        try:
            os.makedirs(new_location)
            shutil.move(self.master_dir, new_location)
            self.info(f"master_dir moved from {self.master_dir} -> {new_location}")
        except OSError as e:
            self.warning(f"Exception while moving master_dir: {e}")

    def list_servers(self) -> list:
        """List all servers in the server_dir"""
        return os.listdir(self.server_dir)

    def load_server(self, server_name: str):
        server_location = os.path.join(self.server_dir, server_name)
        if not os.path.isdir(server_location):
            raise ServerDoesNotExistException(f"Server {server_name} does not exist")

        # search for jar
        potential_jars = [file for file in os.listdir(server_location) if
                          os.path.isfile(os.path.join(server_location, file)) and file.endswith(".jar")]
        server_version = re.search(r"(minecraft_server[.-](?P<version>(.?\d+)+)[.]?jar)",
                                   [file for file in potential_jars if "server" in file][0], re.IGNORECASE).group(
            "version")
        server_is_forge = any(file == self.__jar_name(server_version, is_forge=True) for file in potential_jars)
        server_jar = self.__jar_name(server_version)
        if server_is_forge:
            server_jar = [file for file in potential_jars if file != self.__jar_name(server_version, server_is_forge)][
                0]
        initialized = os.path.isfile(os.path.join(server_location, "server.properties"))
        self.debug(f"Found server @{server_location} v={server_version} is_forge={server_is_forge} "
                   f"start_jar={server_jar} initialized={initialized}")
        return MinecraftServer(server_location=server_location, version=server_version, is_forge=server_is_forge,
                               start_jar_name=server_jar, initialized=initialized)

    def create_server(self, server_name: str, version: str = None, is_forge: bool = False,
                      properties: dict = None, stdout: int = subprocess.DEVNULL, overwrite=False, hard_delete=False,
                      **kwargs):
        if not version:
            version = self.__version_validation(self.get_current_minecraft_version())
        if not properties:
            properties = {}
        properties = kwargs.update(properties)
        self.debug(f"Creating Server {server_name} {version} is_forge?{is_forge} with properties {properties}")
        self.__download_jar(version, is_forge)

        version_comp = version.split(".")[1]
        java = self.java16
        if int(version_comp) <= 14:
            java = self.java8
        if not java:
            java = "java"
        self.info(f"Current java target {java}")
        # TODO: Test backup java version to make sure people with standard installations arent left out

        new_server_location = os.path.join(self.server_dir, server_name)
        if os.path.isdir(new_server_location):
            self.warning(f"Server already exists at {new_server_location}")
            if not overwrite:
                raise ServerAlreadyExistsException(f"Server {server_name} already exists")
            self.info(f"Deleting old server {new_server_location}")
            try:
                if hard_delete:
                    shutil.rmtree(new_server_location)
                else:
                    shutil.rmtree(os.path.join(self.deleted_server_dir, server_name), ignore_errors=True)
                    shutil.move(new_server_location, self.deleted_server_dir)
            except PermissionError:
                logging.warning(f"Server {server_name} is being used by another process")

        os.makedirs(new_server_location, exist_ok=True)
        self.debug(f"Created server @{new_server_location} moving jar file {self.__jar_name(version, is_forge)}")
        shutil.copy2(os.path.join(self.server_jars_dir, self.__jar_name(version, is_forge)),
                     os.path.join(self.server_dir, server_name, self.__jar_name(version, is_forge)))

        # TODO: Find which version of java is needed to run different types of servers
        if is_forge:
            subprocess.run(" ".join([java, "-jar", self.__jar_name(version, is_forge), "--installServer"]),
                           cwd=new_server_location, stdout=stdout)
            jar_name_list = [file for file in os.listdir(new_server_location)
                             if file.startswith("forge") and file.endswith(".jar")
                             and file != self.__jar_name(version, is_forge)]
            if len(jar_name_list) < 1:
                raise JarFileNotFoundException(f"Jar file does not appear in server dir {new_server_location}")
            self.__write_start_batch(new_server_location, ram_allocation=1, jar_name=jar_name_list[0],
                                     java_location=java)
        else:
            self.__write_start_batch(
                new_server_location, ram_allocation=1, jar_name=self.__jar_name(version), java_location=java)

        self.debug(f"Server created @{new_server_location} and populated running start.bat")
        subprocess.run(["start.bat"], cwd=new_server_location, stdout=stdout, shell=True)
        self.debug(f"Server created accepting EULA")

        eula_lines = open(os.path.join(new_server_location, "eula.txt")).readlines()
        open(os.path.join(new_server_location, "eula.txt"), "w").writelines(
            ["eula=true" if str(line).startswith("eula") else line for line in eula_lines])
        self.info(f"Server ready for init")

        server = self.load_server(server_name)
        # TODO: Create start server function which creates a server on a process and enables communication OR takes over the cmd line

    def __write_start_batch(self, server_location: str, ram_allocation: int, jar_name: str,
                            gui: bool = False, java_location: str = "java"):
        with open(os.path.join(server_location, "start.bat"), "w") as writer:
            writer.writelines(MinecraftServer.get_start_batch_lines(ram_allocation=ram_allocation,
                                                                    jar_name=jar_name,
                                                                    gui=gui,
                                                                    java_location=java_location))

    def __download_jar(self, version: str, is_forge=False):
        if not os.path.isfile(os.path.join(self.server_jars_dir, self.__jar_name(version, is_forge=is_forge))):
            if not is_forge:
                self.debug(f"Downloading vanilla jar {version}")
                jar_soup = ServerManager.__get_soup(f"https://mcversions.net/download/{version}").find("a", {
                    "download": f"minecraft_server-{version}.jar"})
                jar_link = jar_soup["href"]
            else:
                self.debug(f"Downloading forge jar {version}")
                jar_soup = ServerManager.__get_soup(
                    f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html").find("div", {
                    "class": "link-boosted"}).find("a")
                jar_link = jar_soup["href"].split("url=")[-1]
            self.info(f"Downloading jar {version} from {jar_link}")
            wget.download(jar_link, os.path.join(self.server_jars_dir, self.__jar_name(version, is_forge=is_forge)))
        self.info(f"Jar {version} already exists not downloading")

    def __jar_name(self, version: str, is_forge: bool = False) -> str:
        version = self.__version_validation(version)
        if not is_forge:
            return f"minecraft_server-{version}.jar"
        return f"forge_installer-{version}.jar"

    def __version_validation(self, version: str):
        version_search = re.search(r"^([.]?(?P<version>([.]?\d+)+))", version, re.IGNORECASE)
        if version_search:
            return version_search.group("version")
        raise IllegalVersionException(f"Version {version} does not appear to contain a version")

    @staticmethod
    def __get_soup(url: str):
        response = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) "
                                                            "Gecko/20100101 Firefox/89.0"})
        if str(response.status_code) == "404":
            raise JarDownloadException(f"Cannot download jar from {url}")
        return BeautifulSoup(requests.get(url).content, "html.parser")

    @staticmethod
    def get_current_minecraft_version():
        return re.search(r"minecraft_server.(?P<version>(.\d*)*).jar",
                         ServerManager.__get_soup(r"https://www.minecraft.net/en-us/download/server").find(
                             "div", {"class": "minecraft-version"}).find("a").text, re.IGNORECASE).group("version")


class MinecraftServer:
    def __init__(self, server_location: str, version: str, is_forge: bool, start_jar_name: str, initialized: bool):
        self.server_location = server_location
        self.server_name = os.path.basename(server_location)
        self.version = version
        self.is_forge = is_forge
        self.start_jar_name = start_jar_name
        self.initialized = initialized

    def write_start_batch(self, ram_allocation: int, gui: bool = False, java_location: str = "java"):
        with open(os.path.join(self.server_location, "start.bat"), "w") as start_file:
            start_file.write(MinecraftServer.get_start_batch_lines(ram_allocation, self.start_jar_name, gui,
                                                                   java_location))

    def get_server_location(self):
        return self.server_location

    def get_server_name(self):
        return self.server_name

    def get_version(self):
        return self.version

    def get_is_forge(self):
        return self.is_forge

    def get_start_jar_name(self):
        return self.start_jar_name

    def get_initialized(self):
        return self.initialized

    @staticmethod
    def get_start_batch_lines(ram_allocation: int, jar_name: str, gui: bool = False, java_location: str = "java"):
        gui_str = "-nogui"
        if gui:
            gui_str = ""
        return f"\"{java_location}\" -Xms{ram_allocation}G -Xmx{ram_allocation}G -jar {jar_name} {gui_str}"


if __name__ == "__main__":
    with ServerManager(r"C:\Users\sprou\Minecraft", logging_level=logging.DEBUG) as manager:
        manager.create_server("TestServerVanilla", overwrite=True, is_forge=False, version="1.12.2", stdout=1)
        manager.create_server("TestServerForge", overwrite=True, is_forge=True, version="1.12.2", stdout=1)

# TODO: Edit a server
# TODO: Run a server
# TODO: Get IP
# TODO: "install" mods
# TODO: Create async functions/compatibility with long operations
