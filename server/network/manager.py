from network.dhcp import DHCP
import subprocess
import nmcli

class NetworkManager():

    dhcp = DHCP()

    def __init__(self):
        nmcli.disable_use_sudo()
 
    def get_all_interfaces(self):
        return nmcli.device()
 
    def get_wan_interface(self):
        for device in nmcli.device.show_all("GENERAL.DEVICE,IP4.GATEWAY,IP6.GATEWAY"):
            if not "GENERAL.DEVICE" in device.keys():
                continue
            if "IP4.GATEWAY" in device.keys() and device["IP4.GATEWAY"]:
                return device["GENERAL.DEVICE"]
            elif "IP6.GATEWAY" in device.keys() and device["IP6.GATEWAY"]:
                return device["GENERAL.DEVICE"]
        return None
 
    def get_physical_interfaces(self):
        return [device.device for device in self.get_all_interfaces() if device.device_type == "ethernet" or device.device_type == "wifi"]
 
    def get_ethernet_interfaces(self):
        return [device.device for device in self.get_all_interfaces() if device.device_type == "ethernet"]
 
    def get_lan_interfaces(self):
        physical = self.get_physical_interfaces()
        wan = self.get_wan_interface()
        if wan in physical:
            physical.remove(wan)
        return physical
 
    def get_interface_status(self, interface : str):
        if not interface in [device.device for device in self.get_all_interfaces()]:
            return None
 
        result = [device.state for device in nmcli.device.status() if device.device == interface][0]
        match result:
            case "connected":
                return "up"
            case "disconnected":
                return "down"
        return None

    def get_ip_address(self, interface : str) -> str:
        return nmcli.device.show(interface, "ip4.address").get("ip4.address[0]")