import pathlib
from setuptools import setup

# the dir containing this file
HERE = pathlib.Path(__file__).parent

# readme
README = (HERE / "README.md").read_text()

# do work
setup(
    name="PyMinecraftServer",
    version="0.5",
    description="Tools for making, editing, and hosting minecraft servers with python. Supports asyncio too.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/CalvinSprouse/PyMinecraftServer",
    author="CalvinSprouse",
    author_email="sprousecal@gmail.com",
    license="MIT",
    classifiers=["Programming Language :: Python :: 3"],
    packages="py_minecraft_server",
    include_package_data=True,
    install_requires=["aiofiles", "aiohttp", "async-timeout", "attrs", "beautifulsoup4", "certifi", "chardet",
                      "coloredlogs", "humanfriendly", "idna", "multidict", "psutil", "pyreadline", "reequests",
                      "soupsieve", "typing-extensions", "urllib3", "wget", "yarl"]
)

# TODO: Follow https://packaging.python.org/ tutorial
