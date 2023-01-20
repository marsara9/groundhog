from wsgiref.simple_server import make_server
from router import Application
import auth
from config import Config
from network import dhcp, vpn, wifi

hostName = "0.0.0.0"
serverPort = 8080

if __name__ == "__main__":
    try:
        if len(auth.enumerate_users()) == 0:
            auth.create_user("admin", "admin")

        config = Config()
        configuration = config.get_all()
        vpn.configure(configuration)
        wifi.configure(configuration)
        dhcp.configure(configuration)

        dhcp_server = dhcp.DHCPServer()
        dhcp_server.restart()

        app = Application(config, dhcp_server)
        app.configure_network()

        with make_server(hostName, serverPort, app) as httpd:
            print(f"Serving on port {serverPort}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
