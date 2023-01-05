from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from datetime import datetime, timedelta
from socketserver import ThreadingMixIn
import os
import urllib.parse
import traceback
import network
import simplejson as json
import bcrypt
import base64

hostName = "0.0.0.0"
serverPort = 8080
 
def create_user(username : str, password : str):
    if not os.path.exists(f"{os.getcwd()}/database/users/{username}"):
        hash = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
 
        with open(f"{os.getcwd()}/database/users/{username}", "wb+") as file:
            file.write(hash)
            file.flush()
 

class MyServer(BaseHTTPRequestHandler):
 
    systemInfo = network.NetworkManager()
 
    def send_basic_error(self, code : int, error : str):
        self.send_response(code)
        self.send_header("Content-Type", "application/josn")
        self.end_headers()
        self.wfile.write(bytes(error, "utf8"))
        return
 
    def send_json_error(self, code : int, message : str, error : Exception = None):
        self.send_response(code)
        self.send_header("Content-Type", "application/josn")
        self.end_headers()
        if __debug__:
            obj = {
                "message": message,
                "error": str(error) if error else None
            }
            self.wfile.write(bytes(json.dumps(obj), "utf8"))
        else:
            self.wfile.write(bytes(json.dumps(message), "utf8"))
        return
 
    def get_ip_address(self):
        if "X-Forwarded-For" in self.headers: 
            return self.headers.get("X-Forwarded-For")
        else:
            return self.client_address[0]
 
    def validate_session(self):
        cookies = SimpleCookie(self.headers.get("Cookie"))
 
        if not ("username" in cookies and "sessionid" in cookies):
            print('\033[93m' + "Auth failed -- no username or sessionid sent" + '\033[0m')
            return False
 
        username = cookies["username"].value
        token = cookies["sessionid"].value
        hashed_token = str(base64.b64decode(token), "utf8")
 
        hashed_password = None
        with open(f"{os.getcwd()}/database/users/{username}", "rb") as file:
            hashed_password = file.read()
 
        decyrpted_token = "".join(chr(ord(a)^ord(b)) for a,b in zip(hashed_token, hashed_password.decode("utf8")))
        print(f"\033[95mAuth Check -- {decyrpted_token}\033[0m")
        token_values = decyrpted_token.split("|")
        if len(token_values) != 3:
            print('\033[93m' + "Auth failed -- mising token values" + '\033[0m')
            return False
        if token_values[0] != username:
            print('\033[93m' + "Auth failed -- username does not match" + '\033[0m')
            return False
        if datetime.fromisoformat(token_values[1]) + timedelta(hours=24) < datetime.now():
            print('\033[93m' + "Auth failed --session has expired" + '\033[0m')
            return False
        if self.get_ip_address() != token_values[2]:
            print('\033[93m' + "Auth failed -- ip address does not match" + '\033[0m')
            return False
        
        return True
 
    def put_base_auth_json(self, put):
        if not self.validate_session():
            self.send_json_error(401, "Not Authorized")
            return

        try:
            length = int(self.headers.get("Content-length"))
            if length == 0:
                self.send_json_error(400)
                return

            body = self.rfile.read(length)
            content = json.loads(body.decode("utf8"))

            put(content)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
        except Exception as e:
            self.send_json_error(500, "There was an error on the server.", e)
            raise e
        return

    def post_auth(self):
        length = int(self.headers.get("Content-length"))
        if length == 0:
            self.send_basic_error(400, "Please enter a username and password")
            return
 
        body = self.rfile.read(length)
        content = json.loads(body.decode("utf8"))
        username = content["username"]
        hashed_password = None
 
        if not os.path.exists(f"{os.getcwd()}/database/users/{username}"):
            self.send_basic_error(401, "Invalid username or password")
            return
 
        with open(f"{os.getcwd()}/database/users/{username}", "rb") as file:
            hashed_password = file.read()
            if not bcrypt.checkpw(content["password"].encode("utf8"), hashed_password):
                self.send_basic_error(401, "Invalid username or password")
                return
 
        now = datetime.now()
        expires = now + timedelta(hours=24)
 
        decrypyed_token = f"{username}|{now.isoformat()}|{self.get_ip_address()}"
        hashed_token = "".join(chr(ord(a)^ord(b)) for a,b in zip(decrypyed_token, hashed_password.decode("utf8")))
        token = str(base64.b64encode(bytes(hashed_token, "utf8")), "utf8")
 
        self.send_response(204)
        self.send_header("Set-Cookie", f"sessionid={token}; Expires={expires.isoformat()}")
        self.send_header("Set-Cookie", f"username={username}")
        self.end_headers()
 
    def put_vpn_configuration(self, configuration : dict[str:any]):
        
        with open(f"{os.getcwd()}/database/config/{self.systemInfo.get_vpn_interface()}.conf", "w+") as file:
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

        self.systemInfo.configure_vpn(self.systemInfo.get_vpn_interface())

        return

    def put_wifi_configuration(self, configuration : dict[str:any]):

        if(configuration["apmode"] == True):
            self.systemInfo.create_access_point(configuration["ssid"], configuration["passphrase"])
        else:
            self.systemInfo.connect_to_wifi(configuration["ssid"], configuration["passphrase"])

        return

    def fix_path(self, filepath : str):
        filepath = filepath.replace("..", "")
        if("?" in filepath):
            filepath = filepath.rsplit("?", 1)[0]
        parts = filepath.split("/")
        if filepath.endswith("/") or not "." in parts[-1]:
            if filepath.endswith("/"):
                filepath += "index.html"
            else:
                filepath += "/index.html"
        return f"ui{filepath}"
 
    def get_file(self, filepath : str):
 
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
 
        try:
            filename = os.getcwd() + os.sep + filepath
            print(f"\033[92mLoading static file '{filename}'\033[0m")
            with open(filename, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", type)
                self.end_headers()
                self.wfile.write(bytes(file.read()))
        except IOError:
            self.send_error(404, f"Not found: '{filename}'")
        return

    def get_base_auth_json(self, get):
        if not self.validate_session():
            self.send_json_error(401, "Not Authorized")
            return

        try:
            object = get()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            result = json.dumps(object)
            self.wfile.write(bytes(result, "utf-8"))
        except Exception as e:
            self.send_json_error(500, "There was an error on the server.", e)
            raise e
        return

    # def get_interfaces(self):

    #     parsed_url = urllib.parse.urlparse(self.path)
    #     query = urllib.parse.parse_qs(parsed_url.query)
 
    #     if "type" in query:
    #         type = query["type"][0]
    #     else:
    #         type = "all"
 
    #     match type:
    #         case "all":
    #             interfaces = self.systemInfo.get_physical_interfaces()
    #         case "ethernet":
    #             interfaces = self.systemInfo.get_ethernet_interfaces()
    #         case "wifi":
    #             interfaces = self.systemInfo.get_wifi_interfaces()
    #         case "lan":
    #             interfaces = self.systemInfo.get_lan_interfaces()
 
    #     return interfaces
 
    def get_status(self):

        wan_interface = self.systemInfo.get_wan_interface()
        wifi_interfaces = self.systemInfo.get_wifi_interfaces()
 
        if len(wan_interface) == 0:
            connection_type = "Unknown"
            internet_status = "down"
        else:
            if wan_interface in wifi_interfaces:
                connection_type = "wifi"
            else:
                connection_type = "ethernet"
            internet_status = self.systemInfo.get_interface_status(wan_interface)
 
        vpn_interface = self.systemInfo.get_vpn_interface()
        vpn_status = self.systemInfo.get_interface_status(vpn_interface)
 
        wifi_status = "down"
        for interface in wifi_interfaces:
            if self.systemInfo.get_interface_status(interface) == "up":
                wifi_status = "up"
 
        dhcp_interfaces = self.systemInfo.get_lan_interfaces()
 
        (ssid,security_type) = self.systemInfo.get_wifi_ssid()
 
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
        return self.systemInfo.get_nearby_access_points()    
 
    def do_GET(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            # if parsed_url.path == "/interfaces":
            #     self.get_base_auth_json(self.get_interfaces)
            if parsed_url.path == "/status":
                self.get_base_auth_json(self.get_status)
            elif parsed_url.path == "/wifi/scan":
                self.get_base_auth_json(self.get_wifi_scan)
            else:
                self.path = self.fix_path(self.path)
                self.get_file(self.path)
        except:
            traceback.print_exc()
            self.send_basic_error(500, "An error occured on the server, please try again")
 
    def do_POST(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            match parsed_url.path:
                case "/auth":
                    self.post_auth()
                case _:
                    self.send_error(404)
        except:
            traceback.print_exc()
            self.send_basic_error(500, "An error occured on the server, please try again")

    def do_PUT(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            match parsed_url.path:
                case "/configuration/vpn":
                    self.put_base_auth_json(self.put_vpn_configuration)
                case "/configuration/wifi":
                    self.put_base_auth_json(self.put_wifi_configuration)
                case _:
                    self.send_error(404)
        except:
            traceback.print_exc()
            self.send_basic_error(500, "An error occured on the server, please try again")
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
 """Handle requests in a separate thread."""
 
if __name__ == "__main__":        
 
    webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    if not os.path.exists(f"{os.getcwd()}/database"):
        os.makedirs(f"{os.getcwd()}/database")
    if not os.path.exists(f"{os.getcwd()}/database/users"):
        os.makedirs(f"{os.getcwd()}/database/users")
    if not os.path.exists(f"{os.getcwd()}/database/config"):
        os.makedirs(f"{os.getcwd()}/database/config")
 
    create_user("admin", "admin")
 
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
 
    webServer.server_close()
    print("Server stopped.")
