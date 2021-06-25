from py_minecraft_server import logger
from py_minecraft_server.utils import soupify_url
import math
import re


def scrape_property_config(is_java_edition: bool = True):
    def get_value_config(type_str: str, default_str: str) -> dict:
        """Retrieves the value configuration only works on java"""
        logger.debug(f"Retrieving value from {type_str.strip()} {default_str.strip()}")
        type_str = type_str.lower().strip()
        default_str = default_str.strip()
        if type_str in ["boolean", "bool"]:
            return {"type": bool, "default": default_str in ["true"], "validator": None}
        elif type_str in ["string", "str"]:
            return {"type": str, "default": default_str, "validator": None}
        elif type_str.split()[0] == "integer":
            int_search = re.search(
                r"\((?P<min>\d+)\W((?P<simple_max>\d+)|\((?P<base>\d+)\^(?P<exponent>\d+)\s*-\s*(?P<subtract>\d+))",
                type_str)
            if int_search:
                int_min = int_search.group('min')
                int_simple_max = int_search.group("simple_max")
                int_base = int_search.group("base")
                int_exponent = int_search.group("exponent")
                int_subtract = int_search.group("subtract")
                if int_exponent:
                    return {"type": int, "default": int(default_str),
                            "validator": lambda num: num >= int(int_min) or num <= int(
                                math.pow(int(int_base), int(int_exponent)) - int(int_subtract))}
            return {"type": int, "default": int(default_str), "validator": None}
        elif type_str == "[more information needed]":
            return {"type": str, "default": None, "validator": None}
        raise ValueError(f"{type_str} not found to be of any type")

    wiki_soup = soupify_url(r"https://minecraft.fandom.com/wiki/Server.properties").find_all(
        "table", {"data-description": "Server properties"})
    if is_java_edition:
        # tables have no defining features so first is java, second is bedrock
        java_soup = wiki_soup[0].find("tbody").find_all("tr")[1:]
        prop_table = {}
        for prop in java_soup:
            prop_soup = prop.find_all("td")
            prop_id = prop.get("id", default=prop_soup[0].get_text()).strip()

            prop_table[prop_id] = get_value_config(prop_soup[1].get_text(), prop_soup[2].get_text()).update(
                {"description": prop_soup[3].get_text().strip()})
        print(prop_table)


if __name__ == "__main__":
    scrape_property_config()
