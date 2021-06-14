class VersionException(Exception):
    def __init__(self, entered_version=None):
        self.entered_version = entered_version

    def get_user_input(self):
        return self.entered_version


class ServerAlreadyExistsException(Exception):
    def __init__(self, attempted_location=None):
        self.attempted_location = attempted_location

    def get_attempted_location(self):
        return self.attempted_location
