from tools.http import HttpTools
from network import dhcp, vpn, wifi
from config import Config
import auth
import os

class Application:

    PASSWORD_LENGTH_REQUIREMENT = 8
    dhcp_server : dhcp.DHCPServer
    debug = False

    def __init__(self, config : Config, dhcp_server : dhcp.DHCPServer, debug : bool):
        self.config = config
        self.dhcp_server = dhcp_server
        self.debug = debug

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
            token = auth.authenticate(username, password, http.request.remote_address)
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

        configuration = self.config.get_safe()
        if "mode" in configuration:
            mode = configuration["mode"]
        else:
            mode = "none"
 
        (ssid,security_type) = wifi.get_wifi_ssid()
 
        return {
            "mode": mode,
            "internetStatus": dhcp.get_wan_interface_status(mode),
            "vpnStatus": vpn.get_interface_status(),
            "wifiStatus": wifi.get_interface_status(),
            "dhcpInterfaces": dhcp.get_lan_interfaces(mode),
            "ssid": ssid,
            "securityType": security_type
        }

    def get_wifi_scan(self):
        return wifi.get_nearby_access_points()

    def post_user_change_password(self, http : HttpTools):
        if http.request.content_length == 0:
            return http.send_json_error(411, "Missing Payload")
        
        if not auth.validate_session_cookies(http.request.cookies, http.request.remote_address):
            return http.send_json_error(401, "Not Authorized")

        if not http.request.validate_json("username", "password", "new-password"):
            return http.send_json_error(400, "Bad Request", Exception("Required content missing from request"))

        content = http.request.jsonBody()

        username = content["username"]
        currnet_password = content["password"]
        new_password = content["password"]["new"]

        if http.request.cookies["username"].value != username:
            return http.send_json_error(403, "Forbidden")

        try:
            token = auth.authenticate(username, currnet_password, http.request.remote_address)
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

        if auth.set_user_password(username, new_password):
            http.start_response("200 OK", [
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600"),
            ])
        else:
            http.send_json_error(406, "The server was unable to change your password at this time.  Please try again later.")

        return []

    def get_simple_configuration(self):
        return [self.config.get_safe()]

    def put_simple_configuration(self, configuration : dict[str:any]):

        old_configuration = self.config.get_all()
        old_configuration.update(configuration)
        configuration = old_configuration

        self.config.update(configuration)
        self.config.save()

        dhcp.configure(self.debug, configuration)
        wifi.configure(self.debug, configuration)
        vpn.configure(configuration)

        self.dhcp_server.restart(self.debug)
