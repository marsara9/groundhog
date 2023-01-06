from network import NetworkManager
from http_tools import HttpTools
import os
import simplejson as json

class Application:

    network_manager = NetworkManager()

    def __call__(self, environ, start_response):
        http = HttpTools(environ, start_response)
        match http.request.method:
            case "GET":
                return self.get(http)
            case "POST":
                return self.post(http)
            case "PUT":
                return self.put(http)
        return http.send_basic_error(404, "Not Found")

    def get(self, http : HttpTools):
        match http.request.path:
            case "/status":
                return http.get_base_auth_json(self.get_status)
            case "/wifi/scan":
                pass
            case _:
                filename = None
                try:
                    filename = http.fix_path(http.request.path)
                    return self.get_file(http, filename)
                except Exception as e:
                    return http.send_basic_error(404, f"Not found: '{filename}'", e)
        return http.send_basic_error(404, "Not Found")

    def post(self, http : HttpTools):
        match http.request.path:
            case "/auth":
                return self.post_auth(http)
        return http.send_basic_error(404, "Not Found")

    def put(self, http : HttpTools):
        match http.request.path:
            case "/configuration/vpn":
                http.put_base_auth_json(self.put_vpn_configuration)
                pass
            case "/configuration/wifi":
                http.put_base_auth_json(self.put_wifi_configuration)
                pass
        return http.send_basic_error(404, "Not Found")

    def post_auth(self, http : HttpTools):
        if http.request.content_length == 0:
            return http.send_json_error(400)

        content = http.request.jsonBody()

        username = content["username"]
        password = content["password"]

        try:
            token = http.auth.authenticate(username, password, http.request.remote_address)
            http.start_response("204 No Content", [
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600"),
                ("Set-Cookie", f"username={username}")
            ])
        except Exception as e:
            http.send_basic_error(401, "Not Authorized", e)
        return []

    def get_file(self, http : HttpTools, filepath : str):
 
        if filepath.endswith(".html"):
            type = "text/html"
        elif filepath.endswith(".js"):
            type = "text/javascript"
        elif filepath.endswith(".css"):
            type = "text/css"
        elif filepath.endswith(".png"):
            type = "image/png"
        elif filepath.endswith(".svg"):
            type = "image/svg+xml"
        else:
            type = None

        filename = os.getcwd() + os.sep + filepath
        print(f"\033[92mLoading static file '{filename}'\033[0m")
        with open(filename, "rb") as file:
            file_content = file.read()
            http.start_response("200 OK", [
                ("Content-Type", type),
                ("Content-Length", str(len(file_content)))
            ])
            return [file_content]

    def get_status(self):

        wan_interface = self.network_manager.get_wan_interface()
        wifi_interfaces = self.network_manager.get_wifi_interfaces()
 
        if len(wan_interface) == 0:
            connection_type = "Unknown"
            internet_status = "down"
        else:
            if wan_interface in wifi_interfaces:
                connection_type = "wifi"
            else:
                connection_type = "ethernet"
            internet_status = self.network_manager.get_interface_status(wan_interface)
 
        vpn_interface = self.network_manager.get_vpn_interface()
        vpn_status = self.network_manager.get_interface_status(vpn_interface)
 
        wifi_status = "down"
        for interface in wifi_interfaces:
            if self.network_manager.get_interface_status(interface) == "up":
                wifi_status = "up"
 
        dhcp_interfaces = self.network_manager.get_lan_interfaces()
 
        (ssid,security_type) = self.network_manager.get_wifi_ssid()
 
        return {
            "connectionType": connection_type,
            "internetStatus": internet_status,
            "vpnStatus": vpn_status,
            "wifiStatus": wifi_status,
            "dhcpInterfaces": dhcp_interfaces,
            "ssid": ssid,
            "securityType": security_type
        }

    def put_vpn_configuration(self, configuration : dict[str:any]):

        self.network_manager.create_vpn_configuration_file(
            self.network_manager.get_vpn_interface(),
            configuration
        )

        self.network_manager.configure_vpn(self.network_manager.get_vpn_interface())

        return

    def put_wifi_configuration(self, configuration : dict[str:any]):

        if(configuration["apmode"] == True):
            self.network_manager.create_access_point(configuration["ssid"], configuration["passphrase"])
        else:
            self.network_manager.connect_to_wifi(configuration["ssid"], configuration["passphrase"])

        return
