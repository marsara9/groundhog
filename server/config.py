from typing import Callable
import yaml
import io
import os
import validators

CONFIG_DIRECTORY = f"{os.getcwd()}/database/config"
DEFAULT_ROOT_CONFIG = f"{CONFIG_DIRECTORY}/groundhod.yml"

class ConfigEntry():

    name : str
    validate: Callable[[str], bool]

    def __init__(self, name : str, validate : Callable[[str], bool], exception_message : str = f"There was an error validating '{name}'."):
        self.name = name
        self.validate = validate
        self.exception_message = exception_message

class Config():

    __config_items : list[ConfigEntry]
    __configuration = {}

    def __init__(self):
        self.__config_items = [
            ConfigEntry(
                "mode", self.__validate_mode, "mode must be one of 'ethernet' or 'wifi'."
            ),
            ConfigEntry(
                "lanip", validators.ipv4_cidr, "lanip was not a valid ip address."
            ),
            ConfigEntry(
                "dns", self.__validate_dns, "dns contianed an item that was not a valid ip address."
            ),
            ConfigEntry(
                "wifi", self.__validate_wifi, "both ssid and passphrase are required, or you may exclude both to disable wifi."
            ),
            ConfigEntry(
                "vpn", self.__validate_vpn
            )
        ]

        if os.path.exists(DEFAULT_ROOT_CONFIG):
            with io.open(DEFAULT_ROOT_CONFIG, "r") as file:
                self.__configuration = yaml.safe_load(file)

    def get_all(self):
        return self.__configuration

    def get_safe(self):
        return self.__configuration

    def save(self):
        if not os.path.exists(DEFAULT_ROOT_CONFIG):
            os.makedirs(DEFAULT_ROOT_CONFIG)

        with io.open(DEFAULT_ROOT_CONFIG, "w+") as file:
            yaml.dump(self.__configuration)

    def update(self, configuration: dict[str:any]):
        for entry in self.__config_items:
            if not entry.validate(configuration[entry.name]):
                raise Exception(entry.exception_message)
            self.__configuration[entry.name] = configuration[entry.name]

    def __validate_mode(self, mode : str) -> bool:
        return mode != "ethernet" and mode != "wifi"

    def __validate_dns(self, dns : list[str]) -> bool:
        for ip in dns:
            if not validators.ipv4(ip):
                return False
        return True

    def __validate_wifi(self, wifi : dict[str:str]) -> bool:
        if len(wifi) == 0:
            return True
        if len(wifi) == 1:
            return False
        if len(wifi) == 2:
            if "ssid" not in wifi or "passphrase" not in wifi:
                return False
            else:
                ssid = wifi["ssid"]
                passphrase = wifi["passphrase"]
                return not self.__is_string_none_or_blank(ssid) and self.__is_string_none_or_blank(passphrase)
        return False

    def __validate_vpn(self, vpn : dict[str:any]) -> bool:
        if ("endpoint" not in vpn or
            "address" not in vpn or
            "keys" not in vpn
        ):
            return False
        elif("public" not in vpn["keys"] or
            "private" not in vpn["keys"] or
            "preshared" not in vpn["keys"]
        ):
            return False
        
        if not validators.domain(vpn["entrypoint"]):
           raise Exception("endpoint was not a valid ip address or domain.")
        if not validators.ipv4(vpn["address"]):
            raise Exception("address was not a valid ip address.")

        return True

    def __is_string_none_or_blank(self, string : str):
        return not(string and string.strip())
