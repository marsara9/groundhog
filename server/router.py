from network import NetworkManager
from http_tools import HttpTools
import os
import simplejson as json

class Application:

    PASSWORD_LENGTH_REQUIREMENT = 8

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
                return http.get_base_auth_json(self.get_wifi_scan)
            case "/simple/configuration":
                return http.get_base_auth_json(self.get_simple_configuration)
            case _:
                filename = None
                try:
                    filename = http.fix_path(http.request.path)
                    if filename != None and len(filename) > 0:
                        return self.get_file(http, filename)
                except Exception as e:
                    return http.send_basic_error(404, f"Not found: '{filename}'", e)
        return http.send_json_error(404, "Not Found")

    def post(self, http : HttpTools):
        match http.request.path:
            case "/auth":
                return self.post_auth(http)
            case "/user/password":
                return self.post_user_change_password(http)
        return http.send_json_error(404, "Not Found")

    def put(self, http : HttpTools):
        match http.request.path:
            case "/simple/configuration":
                return http.put_base_auth_json(self.put_simple_configuration)
        return http.send_json_error(404, "Not Found")

    def post_auth(self, http : HttpTools):
        if http.request.content_length == 0:
            return http.send_json_error(411)

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
 
        dhcp_interfaces = self.network_manager.get_dhcp_configuration()["dhcp"]["interfaces"]
 
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

    def get_wifi_scan(self):
        return self.network_manager.get_nearby_access_points() 

    def post_user_change_password(self, http : HttpTools):
        if http.request.content_length == 0:
            return http.send_json_error(411, "Missing Payload")
        
        if not http.auth.validate_session_cookies(http.request.cookies, http.request.remote_address):
            return http.send_json_error(401, "Not Authorized")

        if not http.request.validate_json("username", "password", "new-password"):
            return http.send_json_error(400, "Bad Request", Exception("Required content missing from request"))

        content = http.request.jsonBody()

        username = content["username"]
        currnet_password = content["password"]
        new_password = content["new-password"]

        if http.request.cookies["username"].value != username:
            return http.send_json_error(403, "Forbidden")

        try:
            token = http.auth.authenticate(username, currnet_password, http.request.remote_address)
        except:
            return http.send_json_error(403, {
                "parameter" : "password",
                "message" : "Current password doesn't match."
            })

        if new_password == currnet_password:
            return http.send_json_error(406, {
                "parameter" : "new-password",
                "message" : "New password cannot be the same as your current password."
            })

        if len(new_password) < self.PASSWORD_LENGTH_REQUIREMENT:
            return http.send_json_error(406, {
                "parameter" : "new-password",
                "message" : "The new password must be at least 8 characters long."
            })

        if http.auth.set_user_password(username, new_password):
            http.start_response("200 OK", [
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600"),
            ])
        else:
            http.send_json_error(406, "The server was unable to change your password at this time.  Please try again later.")

        return []

    def get_simple_configuration(self, include_private_details : bool = False):

        wan_interface = self.network_manager.get_wan_interface()
        wifi_interfaces = self.network_manager.get_wifi_interfaces()
        (ssid,_) = self.network_manager.get_wifi_ssid()

        if len(wan_interface) == 0:
            connection_type = "Unknown"
        else:
            if wan_interface in wifi_interfaces:
                connection_type = "wifi"
            else:
                connection_type = "ethernet"

        # LAN IP is considered to be the IP of the first ethernet interface that isn't
        # directly connected to the internet.  If the device only has a single ethernet
        # interface and it's being used for WAN traffic, then fallback to use the WiFi's
        # adapter's IP address.
        # ip_subnet = next([self.network_manager.get_ip_address(interface) 
        #     for interface in self.network_manager.get_lan_interfaces() 
        #     if self.network_manager.get_ip_address(interface) and 
        #         interface not in self.network_manager.get_wifi_interfaces()
        # ], self.network_manager.get_ip_address(self.network_manager.get_wifi_interfaces()[0]))
        ip_subnet = "10.0.0.72/24"

        vpn_config = self.network_manager.get_vpn_configuration(include_private_details)
        ip_address = ip_subnet.split("/")[0]
        subnet = ip_subnet.split("/")[1]

        wifi_config = {
            "wifi" : {
                "ssid" : ssid
            }
        }

        base_config = {
            "mode" : connection_type,
            "lanip" : ip_address,
            "subnet" : subnet
        }

        base_config.update(vpn_config)
        base_config.update(wifi_config)

        return base_config

    def put_simple_configuration(self, configuration : dict[str:any]):

        configuration["vpn"]["allowed-ips"] = f"{configuration['vpn']['subnet']}/8,8.8.8.8/32,8.8.4.4/32"

        # If there are any missing values (because the user left the field blank)
        # grab the old configuration file as a start, and replace only the fields
        # that were specified.
        old_configuration = self.get_simple_configuration(True)
        old_configuration.update(configuration)
        configuration = old_configuration

        self.network_manager.configure_vpn(configuration)

        wan_interface = self.network_manager.get_wan_interface()
        wifi_interfaces = self.network_manager.get_wifi_interfaces()

        if len(wan_interface) or wan_interface in wifi_interfaces:
            self.network_manager.connect_to_wifi(
                configuration["wifi"]["ssid"],
                configuration["wifi"]["passphrase"]
            )
        else:
            self.network_manager.create_access_point(
                configuration["wifi"]["ssid"],
                configuration["wifi"]["passphrase"]
            )
        
        #self.network_manager.cofigure_dhcp(configuration)
