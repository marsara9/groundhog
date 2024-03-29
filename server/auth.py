from datetime import datetime, timedelta
from http.cookies import SimpleCookie
import base64
import bcrypt
import os

USERS_DIRECTORY = f"{os.getcwd()}/database/users"

def enumerate_users() -> list[str]:
    if not os.path.exists(USERS_DIRECTORY):
        return []

    return [user for user in os.listdir(USERS_DIRECTORY)]

def get_user_hashed_password(username : str) -> bytes:
    user_file = f"{USERS_DIRECTORY}/{username}"

    if os.path.exists(user_file):
        with open(user_file, "rb") as file:
            return file.read()
    else:
        return None

def set_user_password(username : str, password : str) -> bool:
    if not os.path.exists(f"{USERS_DIRECTORY}/{username}"):
        return False
    
    hash = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

    with open(f"{USERS_DIRECTORY}/{username}", "wb+") as file:
        file.write(hash)
        file.flush()

    return True
    

def create_user(username : str, password : str) -> bool:
    if not os.path.exists(USERS_DIRECTORY):
        os.makedirs(USERS_DIRECTORY)

    if not os.path.exists(f"{USERS_DIRECTORY}/{username}"):
        hash = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        with open(f"{USERS_DIRECTORY}/{username}", "wb") as file:
            file.write(hash)
            file.flush()
            return True
    return False

def validate_session_cookies(cookies : SimpleCookie, ip_address : str) -> bool:

    if cookies == None or not ("username" in cookies and "sessionid" in cookies):
        print('\033[93m' + "Auth failed -- no username or sessionid sent" + '\033[0m')
        return False

    username = cookies["username"].value
    token = cookies["sessionid"].value

    return validate_session(username, token, ip_address)

def validate_session(username : str, token : str, ip_address : str) -> bool:
    if username == None or token == None:
        return False

    username = username.lower()

    hashed_token = str(base64.b64decode(token), "utf8")

    hashed_password = get_user_hashed_password(username)

    if hashed_password == None:
        return False

    decyrpted_token = "".join(chr(ord(a)^ord(b)) for a,b in zip(hashed_token, hashed_password.decode("utf8")))
    print(f"\033[95mAuth Check -- {decyrpted_token}\033[0m")
    token_values = decyrpted_token.split("|")
    if len(token_values) != 3:
        print('\033[93m' + "Auth failed -- mising token values" + '\033[0m')
        return False
    if token_values[0] != username:
        print('\033[93m' + "Auth failed -- username does not match" + '\033[0m')
        return False
    if datetime.fromisoformat(token_values[1]) + timedelta(hours=1) < datetime.now():
        print('\033[93m' + "Auth failed --session has expired" + '\033[0m')
        return False
    if ip_address != token_values[2]:
        print('\033[93m' + "Auth failed -- ip address does not match" + '\033[0m')
        return False
    
    return True

def authenticate(username : str, password : str, ip_address : str) -> str:
    
    username = username.lower()
    hashed_password = get_user_hashed_password(username)

    if hashed_password == None:
        raise Exception("Authentication failed; user was not found.")

    if not bcrypt.checkpw(password.encode("utf8"), hashed_password):
        raise Exception("Authentication failed; password did not match")

    return create_auth_token(username, ip_address)

def create_auth_token(username : str, ip_address: str) -> str:

    username = username.lower()
    hashed_password = get_user_hashed_password(username)

    now = datetime.now()

    decrypyed_token = f"{username}|{now.isoformat()}|{ip_address}"
    hashed_token = "".join(chr(ord(a)^ord(b)) for a,b in zip(decrypyed_token, hashed_password.decode("utf8")))
    token = str(base64.b64encode(bytes(hashed_token, "utf8")), "utf8")

    return token    
