import nmcli
import subprocess

def get_interfaces():
    return [device.device for device in nmcli.device() if device.device_type == "wifi"]

def connect_to_wifi(ssid : str, passphrase : str):
    wifi_interfaces = get_interfaces()
    if len(wifi_interfaces) == 0:
        return

    nmcli.radio.wifi_on()
    nmcli.device.wifi_connect(ssid, passphrase, wifi_interfaces[0])
    return

def create_access_point(ssid : str, passphrase : str):
    wifi_interfaces = get_interfaces()
    if len(wifi_interfaces) == 0:
        return

    nmcli.radio.wifi_on()
    nmcli.device.wifi_hotspot(wifi_interfaces[0], ssid=ssid, password=passphrase)
    return

def get_interface_status(interface : str):
    if not interface in [device.device for device in get_interfaces()]:
        return None

    result = [device.state for device in nmcli.device.status() if device.device == interface][0]
    match result:
        case "connected":
            return "up"
        case "disconnected":
            return "down"
    return None

def get_nearby_access_points():
    results = {}
    for signal in nmcli.device.wifi():
        if (signal.ssid is not None and len(signal.ssid) > 0) and (signal.ssid not in results or results[signal.ssid]["strength"] < signal.signal):
            results[signal.ssid] = {
                "security" : signal.security,
                "strength" : signal.signal
            }
    return results

def get_wifi_ssid(self):
    wifi_interfaces = self.get_wifi_interfaces()
    if len(wifi_interfaces) == 0:
        return None

    nmcli_ = subprocess.run(["nmcli", "-t", "-f", "active,ssid,security", "device", "wifi"], stdout=subprocess.PIPE)
    grep = subprocess.run(["grep", "yes"], input=nmcli_.stdout, stdout=subprocess.PIPE)
    awk = subprocess.run(["awk", "-F", ":", "{print $2,$3}"], input=grep.stdout, stdout=subprocess.PIPE)
    result = awk.stdout.decode("utf8").strip("\n").split(",")    
    if len(result) >= 2:
        return result
    else:
        return [None, None]

def configure(configuration : dict[str:any]):
    if(configuration["mode"] == "wifi"):
        connect_to_wifi(
            configuration["wifi"]["ssid"],
            configuration["wifi"]["passphrase"]
        )
    else:
        create_access_point(
            configuration["wifi"]["ssid"],
            configuration["wifi"]["passphrase"]
        )