from network import NetworkManager
from http_tools import HttpTools
import os
import simplejson as json

network_manager = NetworkManager()

class Application:

    def __call__(self, environ, start_response):
        http = HttpTools(environ, start_response)
        match http.method:
            case "GET":
                return self.get(http)
            case "POST":
                return self.post(http)
            case "PUT":
                return self.put(http)
        return http.send_basic_error(404, "Not Found")

    def get(self, http : HttpTools):
        match http.path:
            case "/status":
                return http.get_base_auth_json(self.get_status)
            case "/wifi/scan":
                pass
            case _:
                filename = None
                try:
                    filename = http.fix_path(http.path)
                    return self.get_file(http, filename)
                except Exception as e:
                    return http.send_basic_error(404, f"Not found: '{filename}'", e)
        return http.send_basic_error(404, "Not Found")

    def post(self, http : HttpTools):
        match http.path:
            case "/auth":
                return self.post_auth(http)
        return http.send_basic_error(404, "Not Found")

    def put(self, http : HttpTools):
        match http.path:
            case "/configuration/vpn":
                http.put_base_auth_json(self.put_vpn_configuration)
                pass
            case "/configuration/wifi":
                http.put_base_auth_json(self.put_wifi_configuration)
                pass
        return http.send_basic_error(404, "Not Found")

    def post_auth(self, http : HttpTools):
        length = int(http.environ.get("CONTENT_LENGTH", 0))
        if length == 0:
            return http.send_json_error(400)

        body = http.environ["wsgi.input"].read(length)
        content = json.loads(body.decode("utf8"))

        username = content["username"]
        password = content["password"]

        token = http.auth.authenticate(username, password, http.get_ip_address())
        if token != None:
            http.start_response("204 No Content", [
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600"),
                ("Set-Cookie", f"username={username}")
            ])
        else:
            http.start_response("401 Not Authorized")
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

    def put_vpn_configuration(self, configuration : dict[str:any]):

        if not os.path.exists(f"{os.getcwd()}/database/config"):
            os.makedirs(f"{os.getcwd()}/database/config")
        
        with open(f"{os.getcwd()}/database/config/{network_manager.get_vpn_interface()}.conf", "w+") as file:
            file.write("[Interface]\n")
            file.write(f"PrivateKey = {configuration['privatekey']}\n")
            file.write(f"Address = {configuration['address']}\n")
            file.write(f"DNS = {configuration['dns']}\n")
            file.write("\n\n")
            file.write("[PEER]\n")
            file.write(f"PublicKey = {configuration['publickey']}\n")
            file.write(f"PresharedKey = {configuration['presharedkey']}\n")
            file.write(f"AllowedIPs = {configuration['allowedips']}\n")
            file.write(f"PersistentKeepalive = 0\n")
            file.write(f"Endpoint = {configuration['endpoint']}\n")
            file.flush()

        network_manager.configure_vpn(network_manager.get_vpn_interface())

        return

    def put_wifi_configuration(self, configuration : dict[str:any]):

        if(configuration["apmode"] == True):
            network_manager.create_access_point(configuration["ssid"], configuration["passphrase"])
        else:
            network_manager.connect_to_wifi(configuration["ssid"], configuration["passphrase"])

        return