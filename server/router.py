from network import NetworkManager
from auth import Auth
from http_tools import HttpTools

network_manager = NetworkManager()

class Application:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        match self.environ["REQUEST_METHOD"]:
            case "GET":
                return self.get()
            case "POST":
                return self.post()
            case "PUT":
                return self.put()
        return []

    def get(self):
        http = HttpTools(self.environ, self.start_response)
        match self.environ["PATH_INFO"]:
            case "/status":
                return http.get_base_auth_json(self.get_status)
            case "/wifi/scan":
                pass

    def post(self):
        pass

    def put(self):
        pass

    def post_auth(self):


    def get_status(self):

        wan_interface = network_manager.get_wan_interface()
        wifi_interfaces = network_manager.get_wifi_interfaces()
 
        if len(wan_interface) == 0:
            connection_type = "Unknown"
            internet_status = "down"
        else:
            if wan_interface in wifi_interfaces:
                connection_type = "wifi"
            else:
                connection_type = "ethernet"
            internet_status = network_manager.get_interface_status(wan_interface)
 
        vpn_interface = network_manager.get_vpn_interface()
        vpn_status = network_manager.get_interface_status(vpn_interface)
 
        wifi_status = "down"
        for interface in wifi_interfaces:
            if network_manager.get_interface_status(interface) == "up":
                wifi_status = "up"
 
        dhcp_interfaces = network_manager.get_lan_interfaces()
 
        (ssid,security_type) = network_manager.get_wifi_ssid()
 
        return {
            "connectionType": connection_type,
            "internetStatus": internet_status,
            "vpnStatus": vpn_status,
            "wifiStatus": wifi_status,
            "dhcpInterfaces": dhcp_interfaces,
            "ssid": ssid,
            "securityType": security_type
        }