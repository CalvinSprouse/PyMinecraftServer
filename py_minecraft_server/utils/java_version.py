from py_minecraft_server import logger
import re
import os
import subprocess


def get_java_versions(java_calls=None):
    """ Returns a dict of key=version val=location java versions located on the computer """
    if java_calls is None:
        java_calls = ["java"]

    version_dict = {}
    version_re = re.compile(r"java\s*version\s*\"(?P<ver>\d*\.\d*)\.", re.IGNORECASE)

    def get_version_from_out(output: str) -> str:
        """ Searches line by line cmd outputs to find the java version """
        for ver_line in output.split("\n"):
            version_search = version_re.search(ver_line)
            if version_search:
                return version_search.group("ver")

    def get_subproc_output(args: str, **kwargs) -> str:
        """ returns the stdout + stderr from a subprocess """
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        return str(proc.stdout.decode("utf-8") + proc.stderr.decode("utf-8"))

    # find the java version called by "java" or whatever default call is supplied
    for c in java_calls:
        version = get_version_from_out(get_subproc_output(f"{c} -version"))
        if all([num.isdigit() for num in version.split('.')]):
            version_dict[version] = c

    # find other versions installed on the path
    for j in [[os.path.join(d, e) for e in os.listdir(d) if "java.exe" == e][0] for d in
              [i for i in os.environ["PATH"].split(";") if "java" in i.lower()]]:
        version = get_version_from_out(get_subproc_output(f"{j} -version"))
        if version not in version_dict:
            version_dict[version] = j

    logger.info(f"Found Java versions {[f'{k}={v}' for k, v in version_dict.items()]}")
    return version_dict
