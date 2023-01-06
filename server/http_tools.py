from auth import Auth
from http.client import responses
from http.cookies import SimpleCookie
import simplejson as json

class Request:

    def __init__(self, environ) -> None:
        content_length = self.tryGet(environ, "CONTENT_LENGTH", int, 0)

        self.method = environ["REQUEST_METHOD"]
        self.path = environ["PATH_INFO"]
        self.content_length = content_length
        self.body = environ["wsgi.input"].read(content_length)
        self.cookies = self.tryGet(environ, "HTTP_COOKIE", SimpleCookie, None)

        self.remote_address = self.tryGet(
            environ,
            "HTTP_X_FORWARDED_FOR",
            default=self.tryGet(
                environ,
                "REMOTE_ADDR",
                default=""
            )
        )

    def jsonBody(self):
        return json.loads(self.body.decode("utf8"))

    # Find the given key in environ, then trasform it 
    # using the supplied mapper.  If the key cannot be found
    # or if the value is empty/None or otherwise not present
    # return the default value instead.
    def tryGet(self, environ, key, mapper = lambda it: it, default = None):
        if key in environ and environ[key]:
            return mapper(environ[key])
        else:
            return default
        

class HttpTools:

    auth = Auth()

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        self.request = Request(environ)

    def send_basic_error(self, code : int, message : str, error : Exception = None):
        print(f"Error : {str(error)}")
        self.start_response(f"{code} {responses[code]}", [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(message)))
        ])
        return [message.encode("utf8")]

    def send_json_error(self, code : int, message : str, error : Exception = None):
        #self.environ["wsgi.errors"].write(f"{str(error)}\n")
        self.start_response(f"{code} {responses[code]}", [
            ("Content-Type", "application/json")
        ])
        if __debug__:
            obj = {
                "message": message,
                "error": str(error) if error else None
            }
            return [json.dumps(obj).encode("utf8")]
        else:
            return [json.dumps(message).encode("utf8")]

    def get_base_auth_json(self, get):
        if not self.auth.validate_session_cookies(self.request.cookies, self.request.remote_address):
            return self.send_json_error(401, "Not Authorized")
        try:
            result = json.dumps(get())
            self.start_response("200 OK", [
                ("Content-Type", "application/json"),
                ('Content-Length', str(len(result)))
            ])
            return [result.encode("utf8")]
        except Exception as e:
            return self.send_json_error(500, "There was an error on the server.", e)

    def put_base_auth_json(self, put):
        if not self.auth.validate_session_cookies(self.request.cookies, self.request.remote_address):
            return self.send_json_error(401, "Not Authorized")

        try:
            if self.request.content_length == 0:
                return self.send_json_error(400)                

            content = self.request.jsonBody()

            put(content)

            self.start_response("201 Created", [])
        except Exception as e:
            return self.send_json_error(500, "There was an error on the server.", e)
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
