from wsgiref.simple_server import make_server
from network import dhcp, vpn, wifi
from router import Application
from config import Config
import auth
import nmcli

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
                vpn.configure(configuration)
            if "wifi" in configuration:
                wifi.configure(configuration)
            if "lanip" in configuration:
                dhcp.configure(configuration)

            dhcp_server.restart()

        app = Application(config, dhcp_server)

        with make_server(hostName, serverPort, app) as httpd:
            print(f"Serving on port {serverPort}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
