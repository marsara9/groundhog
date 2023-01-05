import os
import subprocess
import nmcli

class NetworkManager():

    def __init__(self):
        nmcli.disable_use_sudo()
 
    def get_all_interfaces(self):
        return nmcli.device()
 
    def get_wan_interface(self):
        route = subprocess.run(["route"], stdout=subprocess.PIPE)
        default = subprocess.run(["grep", "^default"], input=route.stdout, stdout=subprocess.PIPE)
        grep = subprocess.run(["grep", "-o", "[^ ]*$"], input=default.stdout, stdout=subprocess.PIPE)
        return grep.stdout.decode("utf8").strip("\n")
 
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
        result = awk.stdout.decode("utf8").strip("\n").split(" ")    
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
        return [*set(filter(None, [signal.ssid for signal in nmcli.device.wifi()]))]
 
    def connect_to_wifi(self, ssid : str, passphrase : str):
        wifi_interfaces = self.get_wifi_interfaces()
        if len(wifi_interfaces) == 0:
            return
 
        nmcli.radio.wifi_on()
        nmcli.device.wifi_connect(ssid, passphrase, wifi_interfaces[0])
        return
 
    def configure_vpn(self):
        vpn_interface = self.get_vpn_interface()
        config_path = f"{os.getcwd()}/database/config/{vpn_interface}.conf"
 
        subprocess.call(["nmcli", "connection", "import", "type", "wireguard", "file", config_path])
        nmcli.connection.up(vpn_interface)
        return
 