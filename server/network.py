from dhcp import DHCP
import os
import subprocess
import nmcli
import configparser


class NetworkManager():

    CONFIG_DIRECTORY = f"{os.getcwd()}/database/config"
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
 
    def get_vpn_interface(self):
        return "wg0"
 
    def get_physical_interfaces(self):
        return [device.device for device in self.get_all_interfaces() if device.device_type == "ethernet" or device.device_type == "wifi"]
 
    def get_ethernet_interfaces(self):
        return [device.device for device in self.get_all_interfaces() if device.device_type == "ethernet"]
 
    def get_wifi_interfaces(self):
        return [device.device for device in self.get_all_interfaces() if device.device_type == "wifi"]
 
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
 
    def get_wifi_ssid(self):
        wifi_interfaces = self.get_wifi_interfaces()
        if len(wifi_interfaces) == 0:
            return None
 
        nmcli_ = subprocess.run(["nmcli", "-t", "-f", "active,ssid,security", "device", "wifi"], stdout=subprocess.PIPE)
        grep = subprocess.run(["grep", "yes"], input=nmcli_.stdout, stdout=subprocess.PIPE)
        awk = subprocess.run(["awk", "-F", ":", "{print $2,$3}"], input=grep.stdout, stdout=subprocess.PIPE)
        result = awk.stdout.decode("utf8").strip("\n").split(",")    
        if len(result) >= 2:
            return result
        else:
            return [None, None]
 
    def create_access_point(self, ssid : str, passphrase : str):
        wifi_interfaces = self.get_wifi_interfaces()
        if len(wifi_interfaces) == 0:
            return
 
        nmcli.radio.wifi_on()
        nmcli.device.wifi_hotspot(wifi_interfaces[0], ssid=ssid, password=passphrase)
        return
 
    def get_nearby_access_points(self):
        results = {}
        for signal in nmcli.device.wifi():
            if (signal.ssid is not None and len(signal.ssid) > 0) and (signal.ssid not in results or results[signal.ssid]["strength"] < signal.signal):
                results[signal.ssid] = {
                    "security" : signal.security,
                    "strength" : signal.signal
                }
        return results
 
    def connect_to_wifi(self, ssid : str, passphrase : str):
        wifi_interfaces = self.get_wifi_interfaces()
        if len(wifi_interfaces) == 0:
            return
 
        nmcli.radio.wifi_on()
        nmcli.device.wifi_connect(ssid, passphrase, wifi_interfaces[0])
        return

    def configure_vpn(self, configuration : dict[str:any]):

        vpn_interface = self.get_vpn_interface()
        config_path = f"{self.CONFIG_DIRECTORY}/{vpn_interface}.conf"

        if not os.path.exists(self.CONFIG_DIRECTORY):
            os.makedirs(self.CONFIG_DIRECTORY)
        
        with open(config_path, "w+") as file:
            file.write("[Interface]\n")
            file.write(f"PrivateKey = {configuration['vpn']['keys']['private']}\n")
            file.write(f"Address = {configuration['wan-ip']}\n")
            file.write(f"DNS = {','.join(configuration['dns'])}\n")
            file.write("\n\n")
            file.write("[Peer]\n")
            file.write(f"PublicKey = {configuration['vpn']['keys']['public']}\n")
            file.write(f"PresharedKey = {configuration['vpn']['keys']['preshared']}\n")
            file.write(f"AllowedIPs = {configuration['vpn']['allowed-ips']}\n")
            file.write(f"PersistentKeepalive = 0\n")
            file.write(f"Endpoint = {configuration['vpn']['url']}:{configuration['vpn']['port']}\n")
            file.flush()

        subprocess.call(["nmcli", "connection", "import", "type", "wireguard", "file", config_path])
        nmcli.connection.up(vpn_interface)
        return

    def get_vpn_configuration(self, include_private_details : bool) -> dict[str:any]:

        config_path = f"{self.CONFIG_DIRECTORY}/{self.get_vpn_interface()}.conf"

        if not os.path.exists(config_path):
            return None

        config = configparser.ConfigParser()
        config.read(config_path)

        vpn_endpoint = config["Peer"]["Endpoint"].split(":")
        allowed_ips = config["Peer"]["AllowedIPs"].split(",")
        allowed_ips.remove("8.8.8.8/32")
        allowed_ips.remove("8.8.4.4/32")

        config = {
            "wanip" : config["Interface"]["Address"],
            "dns" : config["Interface"]["DNS"].split(","),
            "vpn" : {
                "url" : vpn_endpoint[0],
                "port" : vpn_endpoint[1],
                "subnet" : allowed_ips[0]
            }
        }

        if(include_private_details):
            config["vpn"]["keys"] = {
                "private" : config["Interface"]["PrivateKey"],
                "private" : config["Peer"]["PublicKey"],
                "private" : config["Peer"]["PresharedKey"],
            }

        return config

    def configure_dhcp(self, configuration : dict[str : any]):
        if not os.path.exists(self.CONFIG_DIRECTORY):
            os.makedirs(self.CONFIG_DIRECTORY)

        config_path = f"{self.CONFIG_DIRECTORY}/dnsmasq.conf"

        ip_addr = configuration["lanip"]
        netmask = "255.255.255.0"
        subnet = DHCP.get_subnet(ip_addr, netmask)
        (range_start, range_end) = DHCP.get_range(subnet, 190, 9)

        dhcp_range = [
            range_start,
            range_end,
            netmask,
            "8h"
        ]

        with open(config_path, "w+") as file:
            file.write("port=0\n")
            file.write(f"dhcp-leasefile={self.CONFIG_DIRECTORY}/dnsmasq.leases\n")
            file.write(f"dhcp-range={','.join(dhcp_range)}\n")
            file.write(f"dhcp-options=6,{','.join(configuration['dns'])}\n")
            # for interface in configuration["dhcp"]["interfaces"]:
            for interface in self.get_lan_interfaces():
                file.write(f"interface={interface}\n")
            file.flush()

        self.dhcp.restart(config_path)
 
    def get_dhcp_configuration(self):
        if not os.path.exists(f"{self.CONFIG_DIRECTORY}/dnsmasq.conf"):
            return None
        
        with open(f"{self.CONFIG_DIRECTORY}/dnsmasq.conf", "r") as file:
            dnsmasq = DHCP.get_config(file.read())

        subnet = DHCP.get_subnet_cidr(
            dnsmasq["dhcp-range"][0],
            dnsmasq["dhcp-range"][2],
        )

        configuration = {
            "dns": dnsmasq["dhcp-options"]["6"],
            "dhcp": {
                "subnet": subnet,
            }
        }

        return configuration

    def get_ip_address(self, interface : str) -> str:
        return nmcli.device.show(interface, "ip4.address").get("ip4.address[0]")