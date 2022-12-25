GitBucket GitBucket
Toggle navigation
Find a repository
Pull requests
Issues
Snippets
@marsara
 Files
 Branches1
 Releases
 Issues
 Pull requests
 Labels
 Priorities
 Milestones
 Wiki
 Settings
  marsara / VPNServer
 VPNServer / vpnserver.py
@MarSara MarSara 8 minutes ago 13 KB adding methods to setup and configure wifi
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from datetime import datetime, timedelta
from socketserver import ThreadingMixIn
import os
import urllib.parse
import subprocess
import traceback
import simplejson as json
import bcrypt
import base64
import nmcli
 
 
hostName = "0.0.0.0"
serverPort = 8080
 
def create_user(username : str, password : str):
    if not os.path.exists(f"./database/users/{username}"):
        hash = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
 
        with open(f"./database/users/{username}", "wb+") as file:
            file.write(hash)
            file.flush()
 
class SystemInformation():
 
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
 
    def configure_vpn(self, config : str):
        vpn_interface = self.get_vpn_interface()
        config_path = f"{os.getcwd()}/database/config/{vpn_interface}.conf"
        with open(config_path, "w+") as file:
            file.write(config)
            file.flush()
 
        subprocess.call(["nmcli", "connection", "import", "type", "wireguard", "file", config_path])
        nmcli.connection.up(vpn_interface)
        return
 
class MyServer(BaseHTTPRequestHandler):
 
    systemInfo = SystemInformation()
 
    def send_basic_error(self, code : int, error : str):
        self.send_response(code)
        self.send_header("Content-Type", "application/josn")
        self.end_headers()
        self.wfile.write(bytes(error, "utf8"))
        return
 
    def send_json_error(self, code : int, object : str):
        self.send_response(code)
        self.send_header("Content-Type", "application/josn")
        self.end_headers()
        self.wfile.write(bytes(json.dump(object), "utf8"))
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
        with open(f"./database/users/{username}", "rb") as file:
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
 
    def post_auth(self):
        length = int(self.headers.get("Content-length"))
        if length == 0:
            self.send_basic_error(400, "Please enter a username and password")
            return
 
        body = self.rfile.read(length)
        content = json.loads(body.decode("utf8"))
        username = content["username"]
        hashed_password = None
 
        if not os.path.exists(f"./database/users/{username}"):
            self.send_basic_error(401, "Invalid username or password")
            return
 
        with open(f"./database/users/{username}", "rb") as file:
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
 
    def get_interfaces(self):
        if not self.validate_session():
            self.send_error(401)
            return
 
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
 
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)
 
        if "type" in query:
            type = query["type"][0]
        else:
            type = "all"
 
        match type:
            case "all":
                result = self.systemInfo.get_physical_interfaces()
            case "ethernet":
                result = self.systemInfo.get_ethernet_interfaces()
            case "wifi":
                result = self.systemInfo.get_wifi_interfaces()
            case "lan":
                result = self.systemInfo.get_lan_interfaces()
 
        interfaces = json.dumps((inf for inf in result), iterable_as_array=True)
        self.wfile.write(bytes(interfaces, "utf-8"))
 
    def get_status(self):
        if not self.validate_session():
            self.send_error(401)
            return
 
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
 
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
 
        result = {
            "connectionType": connection_type,
            "internetStatus": internet_status,
            "vpnStatus": vpn_status,
            "wifiStatus": wifi_status,
            "dhcpInterfaces": dhcp_interfaces,
            "ssid": ssid,
            "securityType": security_type
        }
 
        status = json.dumps(result)
        self.wfile.write(bytes(status, "utf-8"))
 
    def get_wifi_scan(self):
        if not self.validate_session():
            self.send_error(401)
            return
 
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
 
        ssids = self.systemInfo.get_nearby_access_points()
 
        status = json.dumps(ssids)
        self.wfile.write(bytes(status, "utf-8"))
 
    def do_GET(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            if parsed_url.path == "/interfaces":
                self.get_interfaces()
            elif parsed_url.path == "/status":
                self.get_status()
            elif parsed_url.path == "/wifi/scan":
                self.get_wifi_scan()
            else:
                self.path = self.fix_path(self.path)
                self.get_file(self.path)
        except:
            traceback.print_exc()
            self.send_basic_error(500, "An error occured on the server, please try again")
 
    def do_POST(self):
        try:
            match self.path:
                case "/auth":
                    self.post_auth()
                case _:
                    self.send_error(404)
        except:
            traceback.print_exc()
            self.send_basic_error(500, "An error occured on the server, please try again")
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
 """Handle requests in a separate thread."""
 
if __name__ == "__main__":        
    nmcli.disable_use_sudo()
 
    webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
 
    create_user("admin", "admin")
 
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
 
    webServer.server_close()
    print("Server stopped.")
