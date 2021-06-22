from old.exceptions import ServerDoesNotExistException, NoServerLoadedException
from old.naming import get_jar_name
import aiofiles
import asyncio
import logging
import math
import os
import psutil
import re
import requests
import socket
import subprocess

# configure logger
logger = logging.getLogger("py-server")


class ServerLoader:
    def __init__(self, save_location: str):
        """
        A server loader loads a specific server from a save location and edits/runs it.
        :param save_location: The directory servers are saved to.
        """
        self.save_location = os.path.abspath(save_location)
        assert os.path.exists(self.save_location)

        self.server = None
        self.properties = None
        self.mem_allocation = None
        self.server_process = None
        self.server_location = None

        logger.debug(f"Created ServerLoader targeting {self.save_location}")

    async def load_server(self, server_name: str):
        """Set which server to look for from the server save location."""
        self.server = server_name
        self.server_location = os.path.join(self.save_location, server_name)
        if not os.path.exists(self.server_location):
            raise ServerDoesNotExistException()
        await self.load_properties()
        return self

    async def load_properties(self):
        """Load the properties into self.properties dict from server.properties"""
        if not self.server:
            raise NoServerLoadedException()
        properties_contents = await self.get_properties_file_lines()
        self.properties = {line.strip().split("=")[0]: line.strip().split("=")[1] for line in properties_contents
                           if not line.startswith("#")}

    async def save_server(self):
        """Overwrite the server.properties file to updated properties"""
        if not self.server:
            raise NoServerLoadedException()
        properties_contents = await self.get_properties_file_lines()
        async with aiofiles.open(os.path.join(self.server_location, "server.properties"), "w") as properties_file:
            await properties_file.writelines(
                [f"{key.split('=')[0]}={self.properties[key.split('=')[0]]}\n" if "=" in key else key for key in
                 properties_contents])
        logger.debug("Server changes saved")

    async def get_properties_file_lines(self) -> []:
        """Returns the file lines of the server.properties file"""
        if not self.server:
            raise NoServerLoadedException()
        async with aiofiles.open(os.path.join(self.server_location, "server.properties"), "r") as properties_file:
            properties_contents = await properties_file.readlines()
        return properties_contents

    def start_server(self, mem_allocation: int, gui=False):
        """Starts the server as a Popen saved to self.server_process"""
        if not self.server:
            raise NoServerLoadedException()
        gui_str = "nogui"
        if gui:
            gui_str = ""
        self.set_mem_allocation(mem_allocation)

        logger.debug(f"Attempting to start server {self.server} with RAM {mem_allocation}")
        self.server_process = subprocess.Popen(
            f"java -Xms{self.mem_allocation}G -Xmx{self.mem_allocation}G "
            f"-jar {get_jar_name(self.get_current_version())} {gui_str}",
            cwd=self.server_location, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        logger.debug(f"Server {self.server} started with {mem_allocation}GB on {self.get_ip()}")

    def stop_server(self):
        """If the server is running, stop it"""
        if self.is_running():
            try:
                self.get_process().communicate(input=b"stop", timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning(f"Server {self.server} failed to respond to stop command, killing")
                self.get_process().kill()
            logger.debug(f"Server {self.server} stopped")

    def is_running(self):
        """Check if the self.server_process Process is alive"""
        return self.server_process is not None

    def get_process(self):
        """Returns a reference to self.server_process"""
        return self.server_process

    async def server_command(self, command: str):
        """Writes a command into the server"""
        if self.is_running():
            command = bytes(command.strip().encode("unicode-escape").decode() + "\n", "utf8")
            logger.debug(f"Running command to {self.server} {command}")
            # TODO: Capture output and return it and remove the empty wait
            self.get_process().stdin.write(command)
            self.get_process().stdin.flush()
            await asyncio.sleep(5)

    def set_mem_allocation(self, mem_allocation: int):
        """Sets the mem_allocation and ensures it's no more than 50% available RAM"""
        if not self.is_running():
            self.mem_allocation = min(mem_allocation, self.get_max_mem_allocation())

    async def set_property(self, property_name: str, property_val: str, raise_error=False):
        """Change a property of self.properties"""
        # TODO: Add input validation
        if not self.server:
            raise NoServerLoadedException()
        if not self.is_running():
            if property_name not in self.properties:
                logger.warning(f"Key {property_name} does not exist in properties file")
                if raise_error:
                    raise KeyError
            self.properties[property_name] = property_val
            await self.save_server()
            logger.debug(f"Server property {property_name} changed to {property_val}")

    def get_property(self, property_name: str):
        """Return a property from self.properties"""
        return self.properties[property_name]

    def get_current_version(self):
        """Reads the current version from the server jar"""
        if not self.server:
            raise NoServerLoadedException()
        return re.search(r"minecraft_server.(?P<version>(.\d*)*).jar",
                         [jar for jar in os.listdir(self.server_location) if ".jar" in jar][0],
                         re.IGNORECASE).group("version")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_running():
            self.stop_server()

    def __repr__(self):
        return f"Server {self.server} version {self.get_current_version()} running? {self.is_running()}"

    @staticmethod
    def get_max_mem_allocation():
        """Returns the max available memory of the computer"""
        return int((psutil.virtual_memory().available / math.pow(10, 9)) * 0.5)

    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    @staticmethod
    def get_external_ip():
        return requests.get("https://api.ipify.org").text

    @staticmethod
    def get_ip():
        return ServerLoader.get_local_ip(), ServerLoader.get_external_ip()
