from py_minecraft_server.exceptions import *
from py_minecraft_server import OpenProperties
import coloredlogs
import logging
import os
import shutil

SUB_DIRS = ["Servers", "ServerJars", "ServerMods"]


class ServerManager:
    def __init__(self, master_dir: str, logging_handler: logging.Handler = logging.StreamHandler(),
                 logging_level: int = logging.WARNING):
        # ensure dir and sub_dirs exists
        self.master_dir = master_dir
        self.sub_dirs = {}
        for sub_dir in ["Servers", "ServerJars", "ServerMods"]:
            self.sub_dirs[sub_dir] = os.path.join(self.master_dir, sub_dir)
            os.makedirs(self.sub_dirs[sub_dir], exist_ok=True)

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

    def create_server(self, server_name: str, version: str, *args, **kwargs):
        print(kwargs)


if __name__ == "__main__":
    with OpenProperties(r"C:\Users\sprou\Programming\PyMinecraftServer\old\server.properties") as prop_file:
        prop_file.set_properties({"hardcore": "true"}, pvp=False)

# Currently: Can edit properties
# TODO: Create a server
# TODO: Load a server
# TODO: Run a server
# TODO: "install" mods
