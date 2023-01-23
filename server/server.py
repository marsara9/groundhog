from wsgiref.simple_server import make_server
from network import dhcp, vpn, wifi
from router import Application
from config import Config
import auth
import nmcli
import sys

hostName = "0.0.0.0"
serverPort = 8080
debug = False

if __name__ == "__main__":
    try:
        if "debug" in sys.argv:
            debug = True

        nmcli.disable_use_sudo()

        if len(auth.enumerate_users()) == 0:
            auth.create_user("admin", "admin")

        config = Config()
        configuration = config.get_all()

        dhcp_server = dhcp.DHCPServer(config)

        if configuration:
            if "vpn" in configuration and "dns" in configuration:
                if vpn.is_configuration_valid(configuration):
                    vpn.configure(debug, configuration)
                else:
                    print("Configuration Error: VPN missing required values.")
            if "wifi" in configuration:
                if wifi.is_configuration_valid(configuration):
                    wifi.configure(debug, configuration)
                else:
                    print("Configuration Error: WiFi missing required values.")
            if "lanip" in configuration:
                if dhcp.is_configuration_valid(configuration):
                    dhcp.configure(configuration)
                    dhcp_server.restart(debug)
                else:
                    print("Configuration Error: DHCP missing required values.")

        app = Application(config, dhcp_server, debug)

        with make_server(hostName, serverPort, app) as httpd:
            print(f"Serving on port {serverPort}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
