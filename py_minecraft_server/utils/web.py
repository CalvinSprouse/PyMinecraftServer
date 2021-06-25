from bs4 import BeautifulSoup
import requests


def soupify_url(url: str, headers=None):
    """Turns a url into SOUP"""
    return BeautifulSoup(simple_request(url, headers).content, "html.parser")


def simple_request(url: str, headers=None) -> requests.Response:
    """requests.get but with preset headers"""
    if headers is None:
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", }
    return requests.get(url, headers=headers)


def get_forge_url(version: str) -> str:
    """Ensures a constant and streamlined string creation for forge urls"""
    return f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html"


def get_vanilla_url(version: str) -> str:
    """Ensures a constant and streamlined string creation for vanilla urls"""
    return f"https://mcversions.net/download/{version}"
