from wsgiref.simple_server import make_server
from router import Application
from auth import Auth

hostName = "0.0.0.0"
serverPort = 8080

if __name__ == "__main__":
    try:
        auth = Auth()
        if len(auth.enumerate_users()) == 0:
            auth.create_user("admin", "admin")

        app = Application()
        app.configure_network()

        with make_server(hostName, serverPort, app) as httpd:
            print(f"Serving on port {serverPort}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
