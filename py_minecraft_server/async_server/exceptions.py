class ExceedMaxServerCountException(Exception):
    pass


class ServerNameTakenException(Exception):
    pass


class ServerDoesNotExistException(Exception):
    pass


class VersionException(Exception):
    pass


class NoServerLoadedException(Exception):
    pass
