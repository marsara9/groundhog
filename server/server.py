from wsgiref.simple_server import make_server
from network import dhcp, vpn, wifi
from router import Application
from config import Config
import auth
import nmcli
import traceback

hostName = "0.0.0.0"
serverPort = 8080

if __name__ == "__main__":
    try:
        nmcli.disable_use_sudo()

        if len(auth.enumerate_users()) == 0:
            auth.create_user("admin", "admin")

        dhcp_server = dhcp.DHCPServer()

        config = Config()
        configuration = config.get_all()
        if configuration:
            if "vpn" in configuration and "dns" in configuration:
                if vpn.is_configuration_valid(configuration):
                    vpn.configure(configuration)
                else:
                    print("Configuration Error: VPN missing required values.")
            if "wifi" in configuration:
                if wifi.is_configuration_valid(configuration):
                    wifi.configure(configuration)
                else:
                    print("Configuration Error: WiFi missing required values.")
            if "lanip" in configuration:
                if dhcp.is_configuration_valid(configuration):
                    dhcp.configure(configuration)
                else:
                    print("Configuration Error: DHCP missing required values.")

            dhcp_server.restart()

        app = Application(config, dhcp_server)

        with make_server(hostName, serverPort, app) as httpd:
            print(f"Serving on port {serverPort}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
