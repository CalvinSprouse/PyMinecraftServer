import os


class ServerManager:
    def __init__(self, server_save_location: str):
        self.server_save_location = server_save_location
        os.makedirs(self.server_save_location, exist_ok=True)

    create_server = ""
