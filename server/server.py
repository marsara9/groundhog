from wsgiref.simple_server import make_server
from router import Application

if __name__ == "__main__":
    try:
        app = Application()
        with make_server("", 8080, app) as httpd:
            print("Serving on port 8080...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")
