class ServerAlreadyExistsException(Exception):
    pass


class ServerDoesNotExistException(Exception):
    pass


class JarFileNotFoundException(Exception):
    pass


class IllegalVersionException(Exception):
    pass


class JarDownloadException(Exception):
    pass
