from py_minecraft_server import logger
import py_minecraft_server.configuration
import os


class PropertiesManager:
    def __init__(self, server_location: str, backup_filename: str = "backup.properties"):
        """
        A manager of the server.properties file
        :param server_location: The location of the server dir
        :param backup_filename: The name of the backup file, defaults to backup.properties
        """
        self.server_location = server_location
        self.properties_file_location = os.path.join(server_location, "server.properties")
        self.backup_filename = backup_filename
        self.backup_location = os.path.join(os.path.dirname(self.properties_file_location), self.backup_filename)
        if not os.path.isfile(self.properties_file_location):
            raise ValueError(f"{self.properties_file_location} does not point to a file")
        if not os.path.basename(self.properties_file_location) == "server.properties":
            raise ValueError(f"{self.properties_file_location} does not appear to point to a server.properties file")

        # saves a dict of the properties retrieved from the internet
        self.default_property_config = py_minecraft_server.configuration.scrape_property_config()

    def get_properties(self) -> dict:
        """Returns a dict of the properties in the server.properties file"""
        return {line.split("=")[0]: line.split("=")[1].strip() for line in
                open(self.properties_file_location).readlines() if "=" in line}

    def set_properties(self, add_properties: bool = False, ignore_errors: bool = False, **new_properties):
        """
        Accepts keyword input of properties to change can be done as kwargs or as a **{dict}
        :param add_properties: If true will allow keywords that arent already in the server.properties file to be set
        :param ignore_errors: If true will ignore any keys that arent in the server.properties file BUT will not
            write them to the server.properties file unless add_properties is True"""
        logger.debug(f"Changing properties in {self.properties_file_location} to {new_properties}")
        properties = self.get_properties()

        # backup server.properties file
        old_lines = open(self.properties_file_location).readlines()
        open(self.backup_location, "w").writelines(old_lines)

        for prop_key, prop_val in new_properties.items():
            # TODO: Check to ensure this method of value replacing works
            if self.__dict_to_property_tag(prop_key) not in properties:
                if not add_properties:
                    if not ignore_errors:
                        raise ValueError(f"Property {prop_key} not in server.properties")
                    logger.warning(f"Ignoring value {prop_key} as it does not appear in server.properties")
            else:
                logger.debug(f"Changing property {prop_key} to {prop_val} in {self.properties_file_location}")
                properties[prop_key] = prop_val
        # TODO: Apply validation afterwords
        # TODO: Get default values from internet? from something

        # save changes
        new_lines = [f"{line.split('=')[0]}={properties[line.split('=')[0]]}\n" if '=' in line else f"{line.strip()}\n"
                     for line in old_lines]
        open(self.properties_file_location, "w").writelines(new_lines)
        logger.info(f"Properties file {self.properties_file_location} updated backup saved to {self.backup_location}")

    def revert_to_backup(self):
        """Reverts the server.properties file to its most recent backup"""
        backup_lines = open(self.backup_location).readlines()
        open(self.properties_file_location, "w").writelines(backup_lines)
        logger.debug(f"Reverted to backup properties file from {self.backup_location}")
        os.remove(self.backup_location)

    def __dict_to_property_tag(self, dict_key: str) -> tuple[str, str]:
        """Converts the dict key of word_word to a property key of word-word or word.word"""
        return dict_key.replace("_", "-"), dict_key.replace("_", ".")

    def __property_tag_to_dict_key(self, property_tag: str) -> str:
        """Convert the property tag of word.word or word-word to a dict key of word_word"""
        if "." in property_tag:
            return property_tag.replace(".", "_")
        return property_tag.replace("-", "_")
