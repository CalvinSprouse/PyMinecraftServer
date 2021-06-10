"""
CONCEPT:
The class should be defined with:
server_dir = the location where servers will be stored
server_name = name of the server to load/create
Might make two classes a ServerMaker ServerLoader for simplicity

ServerMaker defined with:
server_dir = the location where servers will be stored
server_name = name of the server to create
server_jar_location = by default is none and will download one, if provided then that specifies the version

on init server maker will preform INITIAL creation by accepting the EULA but will hold off on final creation until
properties are configured, I envision the object to be loaded into one of those with statements neither open nor close
will probably do anything but it would make it clean
with ServerMaker(server_dir, server_name, server_version) as maker:
    maker.properties["key"] = val (maybe input validation tied to a hard coded dictionary)

Each server created gets it's folder (as usual) with no modifications except that it will include it's own .jar
The loading device must be able to read the properties file

First step: make server loader/changer
"""
import math
import os
import psutil
import re
import requests
import socket


class ServerLoader:
    def __init__(self, server_dir: str, server_name: str, mem_allocation: float, _override=False, _auto_load=True):
        """
        Create a server loading device which will load the server isn't that great.
        :param server_dir: the location where the server(s) are stored
        :param server_name: the name of the server (should be a subdir of server_dir)
        :param mem_allocation: the amount of memory in GB to allocate towards running the server
        :param _override: if you want to run the server with more than 75% of available RAM
        """
        # ensure the server exists
        self.server_dir = server_dir
        self.server_name = server_name
        self.server_location = os.path.abspath(os.path.join(server_dir, server_name))
        assert os.path.exists(self.server_location)

        # sets the memory allocation to no more than 3/4 the available ram UNLESS the user passes _override=True
        self.mem_allocation = mem_allocation
        if not _override:
            self.mem_allocation = min(mem_allocation, self.get_max_mem_allocation())

        # automatically preform a server properties load
        self.properties = {}
        if _auto_load:
            self.load_server()

    def load_server(self):
        """
        Reads the properties from server.properties with ***dict comprehension***.
        """
        self.properties = {line.strip().split("=")[0]: line.strip().split("=")[1] for line in
                           open(os.path.join(self.server_location, "server.properties"), "r").readlines()
                           if not line.startswith("#")}

    def save_server(self):
        """
        More of my best friend ***dict comprehension*** here to write some lines with style and output to a file (song).
        """
        new_lines = [f"{key.split('=')[0]}={self.properties[key.split('=')[0]]}\n" if "=" in key else key
                     for key in open(os.path.join(self.server_location, "server.properties"), "r").readlines()]
        open(os.path.join(self.server_location, "server.properties"), "w").writelines(new_lines)

    def start_server(self):
        # start the server
        return self

    def stop_server(self):
        # stop the server - should be robust enough to be called twice without error
        pass

    def is_running(self):
        """
        Is the server currently running (cause multithreading maybe)
        :return: True or False
        """

    def change_property(self, property_name: str, val):
        """
        Basically just self.properties[property_name] = val, one day I'll add some input validation.
        :param property_name: key
        :param val: val
        """
        self.properties[property_name] = val

    def set_properties(self, new_properties):
        """
        Overwrite the whole properties dict with one of your own, if you're into that
        :param new_properties: the dict to replace the old one.
        """
        self.properties = new_properties

    def get_properties(self):
        return self.properties

    def set_mem_allocation(self, mem_allocation: float, _override=False):
        """
        Sets the RAM in GB with a max value of 0.75 available RAM. Pass _override=True to get around this
        :param mem_allocation: new RAM in GB
        :param _override: Do you know what you are doing?
        :return new RAM so you can see if it was overridden
        """
        self.mem_allocation = mem_allocation
        if not _override:
            self.mem_allocation = min(self.mem_allocation, self.get_max_mem_allocation())
        return self.get_mem_allocation()

    def get_mem_allocation(self):
        return self.mem_allocation

    def get_current_version(self):
        """
        Analyzes the .jar file found in os.listdir() THERE BETTER ONLY BE ONE DON'T GO ADDING A SECOND
        :return: current version str
        """
        return re.search(r"minecraft_server.(?P<version>(\d*.)*).jar",
                         [jar for jar in os.listdir(self.server_location) if ".jar" in jar][0],
                         re.IGNORECASE).group("version")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_server()
        self.save_server()

    def __repr__(self):
        return f"Server: {self.server_name} running version {self.get_current_version()} with {self.get_mem_allocation()}GB of RAM"

    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    @staticmethod
    def get_external_ip():
        return requests.get("https://api.ipify.org").text

    @staticmethod
    def get_max_mem_allocation():
        return int((psutil.virtual_memory().available / math.pow(10, 9)) * 0.75)


if __name__ == "__main__":
    with ServerLoader("", "training", 100) as loader:
        print(loader.get_current_version())
        print(loader.get_local_ip())
        print(loader.get_external_ip())
        loader.save_server()
