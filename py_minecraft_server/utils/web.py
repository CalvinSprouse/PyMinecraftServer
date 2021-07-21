from bs4 import BeautifulSoup
import requests
import socket


def soupify_url(url: str, headers: dict = None, ignore_errors: bool = False):
    """Turns a url into SOUP"""
    return BeautifulSoup(simple_request(url, headers, ignore_errors).content, "html.parser")


def simple_request(url: str, headers: dict = None, ignore_errors: bool = False) -> requests.Response:
    """requests.get but with preset headers"""
    if headers is None:
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", }
    response = requests.get(url, headers=headers)
    if response.status_code != 200 and not ignore_errors:
        raise ValueError(f"Response status code not 200 for {url}")
    return requests.get(url, headers=headers)


def get_forge_url(version: str) -> str:
    """Ensures a constant and streamlined string creation for forge urls"""
    return f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html"


def get_vanilla_url(version: str) -> str:
    """Ensures a constant and streamlined string creation for vanilla urls"""
    return f"https://mcversions.net/download/{version}"


def get_external_ip():
    """Retrieves the external IP via a website"""
    request = requests.get("https://api.ipify.org")
    if request.status_code == 200:
        return requests.get("https://api.ipify.org").text
    return None


def get_local_ip():
    """Retrieves the local IP via the socket package"""
    return socket.gethostbyname(socket.gethostname())
