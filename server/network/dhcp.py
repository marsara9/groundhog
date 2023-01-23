from config import CONFIG_DIRECTORY
import tools.ip
import subprocess
import nmcli
import os
import re

def get_wan_interface(mode : str) -> str:

    if mode != "ethernet" and mode != "wifi":
        return None

    def get_device_index(device : str) -> int:
        if device is None:
            return -1

        match = re.search(r"\d+$", device)
        if match:
            return int(match.group())
        else:
            return -1

    wan = None
    for device in nmcli.device():
        if device.device_type == mode and wan is None or get_device_index(device.device) < get_device_index(wan):
            if wan is None:
                wan = device.device
            else:
                device_index = get_device_index(device.device)
                wan_index = get_device_index(wan)
                if wan_index < device_index:
                    wan = device.device
    return wan

def get_lan_interfaces(mode : str) -> list[str]:
    wan = get_wan_interface(mode)
    return [device.device for device in nmcli.device() if (device.device_type == "ethernet" or device.device_type == "wifi") and device.device != wan]
    
def get_wan_interface_status(mode : str):
    result = next(iter([device.state for device in nmcli.device.status() if device.device == get_wan_interface(mode)]), None)
    match result:
        case "connected":
            return "up"
        case "disconnected":
            return "down"
    return None

def is_configuration_valid(configuration : dict[str:any]) -> bool:
    if "mode" not in configuration:
        return False
    if "lanip" not in configuration:
        return False
    if "dns" not in configuration:
        return False

def configure(configuration : dict[str:any]):
    if not os.path.exists(CONFIG_DIRECTORY):
        os.makedirs(CONFIG_DIRECTORY)

    config_path = f"{CONFIG_DIRECTORY}/dnsmasq.conf"

    ip_addr_cidr = configuration["lanip"]
    subnet = tools.ip.get_subnet_ip_cidr(ip_addr_cidr)
    prefix = tools.ip.get_subnet_prefix(ip_addr_cidr)
    (range_start, range_end) = tools.ip.get_range(f"{subnet}/{prefix}", 190, 9)

    dhcp_range = [
        range_start,
        range_end,
        "8h"
    ]

    with open(config_path, "w+") as file:
        file.write("port=0\n")
        file.write("dhcp-authoritative\n")
        file.write(f"dhcp-leasefile={CONFIG_DIRECTORY}/dnsmasq.leases\n")
        file.write(f"dhcp-range={','.join(dhcp_range)}\n")
        file.write(f"dhcp-option=6,{','.join(configuration['dns'])}\n")
        for interface in get_lan_interfaces(configuration["mode"]):
            file.write(f"interface={interface}\n")
        file.flush()

class DHCPServer():

    __process = None
        
    def restart(self, debug : bool):
        if self.__process:
            self.__process.terminate()
            self.__process.wait()

        config_path = f"{CONFIG_DIRECTORY}/dnsmasq.conf"

        if not debug:
            self.__process = subprocess.Popen([
                "dnsmasq",
                "-C",
                config_path
            ])
    