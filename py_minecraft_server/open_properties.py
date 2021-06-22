from dataclasses import dataclass
import math
import re
import os


class OpenProperties:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_file_opener(self, mode: str = "r"):
        return open(self.filename, mode)

    def get_properties(self):
        return {line.strip().split("=")[0].replace("-", "_"): line.strip().split("=")[1] for line in
                self.get_file_opener().readlines() if "=" in line and not line.startswith("#")}

    def set_properties(self, properties_dict: dict = None, **kwargs):
        real_properties = self.get_properties()
        if properties_dict is None:
            properties_dict = {}
        for key, val in {**kwargs, **properties_dict}.items():
            real_properties[key] = str(val)
        self.__save_properties(real_properties)

    def __save_properties(self, properties_dict: dict):
        lines = [f"{line.split('=')[0].replace('-', '_').strip()}={properties_dict[line.split('=')[0].replace('-', '_').strip()]}\n"
                 if "=" in line else line for line in self.get_file_opener().readlines()]
        self.get_file_opener("w").writelines(lines)




"""
Years of academy training wasted, cant set values afterword from a dict
@dataclass
class ServerProperties:
    def __set_string(self, value):
        if not isinstance(value, str):
            raise TypeError(f"Value '{value}' must be a string")
        return value.strip()

    def __set_int_string(self, value):
        test_value = self.__set_string(value)
        if not test_value.isdigit():
            raise TypeError(f"Value '{value}' must be a string of digits")
        return test_value

    def __set_bool_string(self, value, true_list: list = None, false_list: list = None):
        if not true_list:
            true_list = ["t", "true"]
        if not false_list:
            false_list = ["f", "false"]
        test_value = self.__set_string(value).lower()
        if test_value in true_list:
            return "true"
        elif test_value in false_list:
            return "false"
        raise ValueError(f"Value '{value}' contains no bool-like patterns {true_list} {false_list}")

    def __int_string_between(self, value, val_min: int = None, val_max: int = None):
        test_val = int(self.__set_int_string(value))
        if val_min:
            if test_val < val_min:
                raise ValueError(f"Value '{value}' can not be less than val_min {val_min}")
        if val_max:
            if test_val > val_max:
                raise ValueError(f"Value '{value}' can not be more than val_max {val_max}")
        return str(test_val)

    def __specific_strings(self, value, legal_strings: list, ignorecase=True):
        test_value = self.__set_string(value)
        if ignorecase:
            for string in legal_strings:
                if test_value.lower() == string.lower():
                    return test_value
            raise ValueError(f"Value '{value}' must be one of these {legal_strings}")
        else:
            if test_value not in legal_strings:
                raise ValueError(f"Value '{value}' must be one of these {legal_strings}")
            return test_value

    def __get_generator_settings(self):
        return self.__dict__.get("generator-settings")

    def __set_generator_settings(self, value):
        self.__dict__["generator-settings"] = self.__set_string(value)

    generator_settings: str = property(__get_generator_settings, __set_generator_settings)

    def __get_op_permission_level(self):
        return self.__dict__.get("op-permission-level")

    def __set_op_permission_level(self, value):
        self.__dict__["op-permission-level"] = self.__int_string_between(value, 0, 4)

    op_permission_level: str = property(__get_op_permission_level, __set_op_permission_level)

    def __get_allow_nether(self):
        return self.__dict__.get("allow-nether")

    def __set_allow_nether(self, value):
        self.__dict__["allow-nether"] = self.__set_bool_string(value)

    allow_nether: str = property(__get_allow_nether, __set_allow_nether)

    def __get_level_name(self):
        return self.__dict__.get("level-name")

    def __set_level_name(self, value):
        self.__dict__["level-name"] = self.__set_string(value)

    level_name: str = property(__get_level_name, __set_level_name)

    def __get_enable_query(self):
        return self.__dict__.get("enable-query")

    def __set_enable_query(self, value):
        self.__dict__["enable-query"] = self.__set_bool_string(value)

    enable_query: str = property(__get_enable_query, __set_enable_query)

    def __get_allow_flight(self):
        return self.__dict__.get("allow-flight")

    def __set_allow_flight(self, value):
        self.__dict__["allow-flight"] = self.__set_bool_string(value)

    allow_flight: str = property(__get_allow_flight, __set_allow_flight)

    def __get_prevent_proxy_connections(self):
        return self.__dict__.get("prevent-proxy-connections")

    def __set_prevent_proxy_connections(self, value):
        self.__dict__["prevent-proxy-connections"] = self.__set_bool_string(value)

    prevent_proxy_connections: str = property(__get_prevent_proxy_connections, __set_prevent_proxy_connections)

    def __get_server_port(self):
        return self.__dict__.get("server-port")

    def __set_server_port(self, value):
        self.__dict__["server-port"] = self.__int_string_between(value, 1, int(math.pow(2, 16) - 2))

    server_port: str = property(__get_server_port, __set_server_port)

    def __get_max_world_size(self):
        return self.__dict__.get("max-world-size")

    def __set_max_world_size(self, value):
        self.__dict__["max-world-size"] = self.__int_string_between(value, 1, 29999984)

    max_world_size: str = property(__get_max_world_size, __set_max_world_size)

    def __get_level_type(self):
        return self.__dict__.get("level-type")

    def __set_level_type(self, value):
        self.__dict__["level-type"] = self.__specific_strings(value, legal_strings=["default", "flat", "largeBiomes",
                                                                                    "amplified", "buffet",
                                                                                    "default_1_1", "customized"])

    level_type: str = property(__get_level_type, __set_level_type)

    def __get_enable_rcon(self):
        return self.__dict__.get("enable-rcon")

    def __set_enable_rcon(self, value):
        self.__dict__["enable-rcon"] = self.__set_bool_string(value)

    enable_rcon: str = property(__get_enable_rcon, __set_enable_rcon)

    def __get_level_seed(self):
        return self.__dict__.get("level-seed")

    def __set_level_seed(self, value):
        self.__dict__["level-seed"] = self.__set_string(value)

    level_seed: str = property(__get_level_seed, __set_level_seed)

    def __get_force_gamemode(self):
        return self.__dict__.get("force-gamemode")

    def __set_force_gamemode(self, value):
        self.__dict__["force-gamemode"] = self.__set_bool_string(value)

    force_gamemode: str = property(__get_force_gamemode, __set_force_gamemode)

    def __get_server_ip(self):
        return self.__dict__.get("server-ip")

    def __set_server_ip(self, value):
        test_value = self.__set_string(value)
        if re.search(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", test_value):
            self.__dict__["server-ip"] = self.__set_string(value)

    server_ip: str = property(__get_server_ip, __set_server_ip)

    def __get_network_compression_threshold(self):
        return self.__dict__.get("network-compression-threshold")

    def __set_network_compression_threshold(self, value):
        self.__dict__["network-compression-threshold"] = self.__int_string_between(value, -1, 256)

    network_compression_threshold: str = property(__get_network_compression_threshold,
                                                  __set_network_compression_threshold)

    def __get_max_build_height(self):
        return self.__dict__.get("max-build-height")

    def __set_max_build_height(self, value):
        self.__dict__["max-build-height"] = self.__int_string_between(value, 1, 256)

    max_build_height: str = property(__get_max_build_height, __set_max_build_height)

    def __get_spawn_npcs(self):
        return self.__dict__.get("spawn-npcs")

    def __set_spawn_npcs(self, value):
        self.__dict__["spawn-npcs"] = self.__set_bool_string(value)

    spawn_npcs: str = property(__get_spawn_npcs, __set_spawn_npcs)

    def __get_white_list(self):
        return self.__dict__.get("white-list")

    def __set_white_list(self, value):
        self.__dict__["white-list"] = self.__set_bool_string(value)

    white_list: str = property(__get_white_list, __set_white_list)

    def __get_spawn_animals(self):
        return self.__dict__.get("spawn-animals")

    def __set_spawn_animals(self, value):
        self.__dict__["spawn-animals"] = self.__set_bool_string(value)

    spawn_animals: str = property(__get_spawn_animals, __set_spawn_animals)

    def __get_hardcore(self):
        return self.__dict__.get("hardcore")

    def __set_hardcore(self, value):
        self.__dict__["hardcore"] = self.__set_bool_string(value)

    hardcore: str = property(__get_hardcore, __set_hardcore)

    def __get_snooper_enabled(self):
        return self.__dict__.get("snooper-enabled")

    def __set_snooper_enabled(self, value):
        self.__dict__["snooper-enabled"] = self.__set_bool_string(value)

    snooper_enabled: str = property(__get_snooper_enabled, __set_snooper_enabled)

    def __get_resource_pack_sha1(self):
        return self.__dict__.get("resource-pack-sha1")

    def __set_resource_pack_sha1(self, value):
        self.__dict__["resource-pack-sha1"] = self.__set_string(value)

    resource_pack_sha1: str = property(__get_resource_pack_sha1, __set_resource_pack_sha1)

    def __get_online_mode(self):
        return self.__dict__.get("online-mode")

    def __set_online_mode(self, value):
        self.__dict__["online-mode"] = self.__set_bool_string(value)

    online_mode: str = property(__get_online_mode, __set_online_mode)

    def __get_resource_pack(self):
        return self.__dict__.get("resource-pack")

    def __set_resource_pack(self, value):
        self.__dict__["resource-pack"] = self.__set_string(value)

    resource_pack: str = property(__get_resource_pack, __set_resource_pack)

    def __get_pvp(self):
        return self.__dict__.get("pvp")

    def __set_pvp(self, value):
        self.__dict__["pvp"] = self.__set_bool_string(value)

    pvp: str = property(__get_pvp, __set_pvp)

    def __get_difficulty(self):
        return self.__dict__.get("difficulty")

    def __set_difficulty(self, value):
        self.__dict__["difficulty"] = self.__specific_strings(value, legal_strings=["peaceful", "easy", "normal",
                                                                                    "hard", "0", "1", "2", "3"])

    difficulty: str = property(__get_difficulty, __set_difficulty)

    def __get_enable_command_block(self):
        return self.__dict__.get("enable-command-block")

    def __set_enable_command_block(self, value):
        self.__dict__["enable-command-block"] = self.__set_bool_string(value)

    enable_command_block: str = property(__get_enable_command_block, __set_enable_command_block)

    def __get_gamemode(self):
        return self.__dict__.get("gamemode")

    def __set_gamemode(self, value):
        self.__dict__["gamemode"] = self.__specific_strings(value, legal_strings=["survival", "creative", "adventure",
                                                                                  "spectator", "0", "1", "2", "3"])

    gamemode: str = property(__get_gamemode, __set_gamemode)

    def __get_player_idle_timeout(self):
        return self.__dict__.get("player-idle-timeout")

    def __set_player_idle_timeout(self, value):
        self.__dict__["player-idle-timeout"] = self.__set_int_string(value)

    player_idle_timeout: str = property(__get_player_idle_timeout, __set_player_idle_timeout)

    def __get_max_players(self):
        return self.__dict__.get("max-players")

    def __set_max_players(self, value):
        self.__dict__["max-players"] = self.__int_string_between(value, 0, int(math.pow(2, 31) - 1))

    max_players: str = property(__get_max_players, __set_max_players)

    def __get_max_tick_time(self):
        return self.__dict__.get("max-tick-time")

    def __set_max_tick_time(self, value):
        self.__dict__["max-tick-time"] = self.__int_string_between(value, 0, int(math.pow(2, 63) - 1))

    max_tick_time: str = property(__get_max_tick_time, __set_max_tick_time)

    def __get_spawn_monsters(self):
        return self.__dict__.get("spawn-monsters")

    def __set_spawn_monsters(self, value):
        self.__dict__["spawn-monsters"] = self.__set_bool_string(value)

    spawn_monsters: str = property(__get_spawn_monsters, __set_spawn_monsters)

    def __get_view_distance(self):
        return self.__dict__.get("view-distance")

    def __set_view_distance(self, value):
        self.__dict__["view-distance"] = self.__int_string_between(value, 3, 32)

    view_distance: str = property(__get_view_distance, __set_view_distance)

    def __get_generate_structures(self):
        return self.__dict__.get("generate-structures")

    def __set_generate_structures(self, value):
        self.__dict__["generate-structures"] = self.__set_bool_string(value)

    generate_structures: str = property(__get_generate_structures, __set_generate_structures)

    def __get_motd(self):
        return self.__dict__.get("motd")

    def __set_motd(self, value):
        self.__dict__["motd"] = self.__set_string(value)

    motd: str = property(__get_motd, __set_motd)


def create_dataclass_structure(server_properties_location: str):
    for prop in open(server_properties_location).readlines():
        if not prop.startswith("#"):
            name = prop.split("=")[0].replace("-", "_").strip()
            print(f"def __get_{name}(self):\n\treturn self.__dict__.get(\"{name.replace('_', '-')}\")\n")
            print(f"def __set_{name}(self, value):\n\tself.__dict__[\"{name.replace('_', '-')}\"] "
                  f"= self.__set_string(value)\n")
            print(f"{name}: str = property(__get_{name}, __set_{name})\n\n")
"""
