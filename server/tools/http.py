from http.client import responses
from http.cookies import SimpleCookie
import auth
import simplejson as json
import traceback

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

    def validate_json(self, *keys) -> bool:
        content = self.jsonBody()
        for key in keys:
            if not key in content:
                return False
        return True

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

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        self.request = Request(environ)

    def print_error(self,error : Exception):
        stack = traceback.format_exception(error)
        for entry in stack:
            print(f"\033[91m{entry}\033[0m")

    def send_basic_error(self, code : int, message : str, error : Exception = None):

        if error != None:
            self.print_error(error)
        
        self.start_response(f"{code} {responses[code]}", [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(message)))
        ])

        return [message.encode("utf8")]

    def send_json_error(self, code : int, message : any = None, error : Exception = None):

        if error != None:
            self.print_error(error)

        self.start_response(f"{code} {responses[code]}", [
            ("Content-Type", "application/json")
        ])

        if message == None:
            message = {
                "message" : responses[code]
            }
        elif not isinstance(message, dict):
            message = {
                "message" : message
            }

        message["code"] = code

        if __debug__:
            message["error"] = str(error) if error else None

        return [json.dumps(message).encode("utf8")]

    def get_base_auth_json(self, get):
        if not auth.validate_session_cookies(self.request.cookies, self.request.remote_address):
            return self.send_json_error(401, "Not Authorized")
        try:
            username = self.request.cookies["username"].value
            token = auth.create_auth_token(username, self.request.remote_address)

            result = json.dumps(get())

            self.start_response("200 OK", [
                ("Content-Type", "application/json"),
                ('Content-Length', str(len(result))),
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600"),
            ])
            return [result.encode("utf8")]
        except Exception as e:
            return self.send_json_error(500, "There was an error on the server.", e)

    def put_base_auth_json(self, put):
        if not auth.validate_session_cookies(self.request.cookies, self.request.remote_address):
            return self.send_json_error(401, "Not Authorized")

        try:
            if self.request.content_length == 0:
                return self.send_json_error(411)

            username = self.request.cookies["username"].value
            token = auth.create_auth_token(username, self.request.remote_address)

            content = self.request.jsonBody()

            put(content)

            self.start_response("201 Created", [
                ("Set-Cookie", f"sessionid={token}; Max-Age=3600")
            ])
        except Exception as e:
            return self.send_json_error(500, "There was an error on the server.", e)
        return []

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
