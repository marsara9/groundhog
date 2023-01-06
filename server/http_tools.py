from auth import Auth
import simplejson as json

class HttpTools:

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    auth = Auth()

    def send_json_error(self, code : int, message : str, error : Exception = None):
        self.start_response(f"{code}", [
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
 
    def get_ip_address(self):
        if "HTTP_X_FORWARDED_FOR" in self.environ: 
            return self.environ["HTTP_X_FORWARDED_FOR"].split(',')[-1].strip()
        else:
            return self.environ["REMOTE_ADDR"]

    def get_base_auth_json(self, get):
        if not self.auth.validate_session():
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
        if not self.auth.validate_session():
            return self.send_json_error(401, "Not Authorized")

        try:
            length = int(self.environ.get("CONTENT_LENGTH", 0))
            if length == 0:
                return self.send_json_error(400)                

            body = self.environ["wsgi.input"].read(length)
            content = json.loads(body.decode("utf8"))

            put(content)

            self.start_response("201 Created", [])
        except Exception as e:
            return self.send_json_error(500, "There was an error on the server.", e)
        return
