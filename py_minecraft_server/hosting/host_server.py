import string

from py_minecraft_server import logger
from py_minecraft_server.commands import ServerRCON, ServerQuery
from py_minecraft_server.configuration import PropertiesManager
from py_minecraft_server.utils import get_external_ip, get_local_ip
import asyncio
import os
import random
import subprocess


class ServerHost:
    def __init__(self, server_location: str, ram_allocation: int, server_jar_name: str, java_ref: str = "java"):
        self.server_location = server_location
        self.ram_allocation = ram_allocation
        self.server_jar_name = server_jar_name
        self.java_ref = java_ref
        self.server_process = None
        self.server_rcon = None
        self.server_query = None
        self.server_command = None
        if not os.path.isdir(server_location):
            raise ValueError(f"Server location {server_location} not a directory")
        logger.info(f"Instantiated ServerHost @{server_location} ram{ram_allocation}GB java={java_ref}")

    def write_start_batch(self, gui: bool = False):
        gui_str = "nogui"
        if gui_str:
            gui_str = ""
        self.server_command = (f"\"{self.java_ref}\" -Xms{self.ram_allocation}G -Xmx{self.ram_allocation}G "
                               f"-jar {self.server_jar_name} {gui_str}")
        logger.info(
            f"Server command for ServerHost {os.path.basename(self.server_location)} set to {self.server_command}")
        with open(os.path.join(self.server_location, "start.bat"), "w") as writer:
            writer.write(f"{self.server_command}\npause")

    async def start_server(self, stdout: bool = False):
        self.write_start_batch()
        if not stdout:
            stdout = subprocess.DEVNULL
        else:
            stdout = None

        properties = PropertiesManager(os.path.join(self.server_location, "server.properties"))
        if properties.get_properties()["enable-rcon"].strip() in ["false"]:
            properties.set_properties(**{"enable-rcon": "true"})
        if properties.get_properties()["enable-query"].strip() in ["false"]:
            properties.set_properties(**{"enable-query": "true"})
        if properties.get_properties()["rcon.password"].strip() == "":
            properties.set_properties(
                **{"rcon.password": "".join(random.choice(string.ascii_letters) for _ in range(10))})
        properties = properties.get_properties()

        logger.debug(f'rcon={properties["enable-rcon"]} query={properties["enable-query"]} '
                     f'rcon pass={properties["rcon.password"]} rcon port={properties["rcon.port"]}')
        logger.info(f"Starting server {os.path.basename(self.server_location)} on separate process")

        self.server_process = subprocess.Popen(self.server_command, cwd=self.server_location, shell=True,
                                               stdout=stdout)
        # TODO: Find less arbitrary way to ensure server is hosted
        await asyncio.sleep(10)
        self.server_rcon = ServerRCON(host="localhost", password=properties["rcon.password"].strip())
        self.server_query = ServerQuery(host="localhost")
        logger.info(f"Server hosted on local:{get_local_ip()} external:{get_external_ip()}")
        return self.server_process

    async def stop_server(self):
        logger.info(f"Sending stop command to server @{os.path.basename(self.server_location)}")
        self.server_rcon.command("stop")
        while self.server_process.poll is None:
            await asyncio.sleep(0.25)
        self.server_process = None
        self.server_rcon = None
        self.server_query = None
        logger.info(f"Server stopped @{os.path.basename(self.server_location)}")

    def get_rcon(self):
        return self.server_rcon

    def get_query(self):
        return self.server_query

    def is_server_alive(self):
        return self.server_process.poll is None

    def get_server_rcon(self):
        return self.server_rcon

    def get_server_query(self):
        return self.server_query
