from config import CONFIG_DIRECTORY
import tools.ip
import subprocess
import nmcli
import os
import re

def get_wan_interface(mode : str) -> str:

    def get_device_index(device : str) -> int:
        match = re.search(r'\d+$', device)
        return int(match.group()) if match else None

    wan = None
    for device in nmcli.device():
        if device.device_type == mode and wan is None or get_device_index(device.device) < get_device_index(wan):
            wan = device.device
    return wan

def get_lan_interfaces(mode : str) -> list[str]:
    wan = get_wan_interface(mode)
    return [device.device for device in nmcli.device() if (device.device_type == "ethernet" or device.device_type == "wifi") and device.device != wan]
    

def configure(configuration : dict[str:any]):
    if not os.path.exists(CONFIG_DIRECTORY):
        os.makedirs(CONFIG_DIRECTORY)

    config_path = f"{CONFIG_DIRECTORY}/dnsmasq.conf"

    ip_addr_cidr = configuration["lanip"]
    subnet = tools.ip.get_subnet_ip_cidr(ip_addr_cidr)
    (range_start, range_end) = tools.ip.get_range(subnet, 190, 9)

    dhcp_range = [
        range_start,
        range_end,
        "8h"
    ]

    with open(config_path, "w+") as file:
        file.write("port=0\n")
        file.write(f"dhcp-leasefile={CONFIG_DIRECTORY}/dnsmasq.leases\n")
        file.write(f"dhcp-range={','.join(dhcp_range)}\n")
        file.write(f"dhcp-options=6,{','.join(configuration['dns'])}\n")
        for interface in get_lan_interfaces(configuration["mode"]):
            file.write(f"interface={interface}\n")
        file.flush()

class DHCPServer():

    __process = None
        
    def restart(self):
        if self.__process:
            self.__process.terminate()
            self.__process.wait()

        config_path = f"{CONFIG_DIRECTORY}/dnsmasq.conf"

        self.__process = subprocess.Popen([
            "dnsmasq",
            "-C",
            config_path
        ])
    