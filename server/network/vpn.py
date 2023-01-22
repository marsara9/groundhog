from config import CONFIG_DIRECTORY
import subprocess
import nmcli
import os

def get_interface():
        return "wg0"

def get_interface_status():
    result = next(iter([device.state for device in nmcli.device.status() if device.device == get_interface()]), "disconnected")
    match result:
        case "connected":
            return "up"
        case "disconnected":
            return "down"
    return None

def is_configuration_valid(configuration : dict[str:any]) -> bool:
    if "dns" not in configuration:
        return False
    if "vpn" not in configuration:
        if "endpoint" not in configuration["vpn"]:
            return False
        if "address" not in configuration["vpn"]:
            return False
        if "subnet" not in configuration["vpn"]:
            return False
        if "keys" not in configuration["vpn"]:
            if "public" not in configuration["vpn"]["keys"]:
                return False
            if "private" not in configuration["vpn"]["keys"]:
                return False
            if "preshared" not in configuration["vpn"]["keys"]:
                return False
    return True

def configure(configuration : dict[str:any]):
    vpn_interface = get_interface()
    config_path = f"{CONFIG_DIRECTORY}/{vpn_interface}.conf"

    if not os.path.exists(CONFIG_DIRECTORY):
        os.makedirs(CONFIG_DIRECTORY)

    allowed_ips = [f"{ip}/32" for ip in configuration["dns"]]
    allowed_ips.append(configuration["vpn"]["subnet"])
    
    with open(config_path, "w+") as file:
        file.write("[Interface]\n")
        file.write(f"PrivateKey = {configuration['vpn']['keys']['private']}\n")
        file.write(f"Address = {configuration['vpn']['address']}\n")
        file.write(f"DNS = {','.join(configuration['dns'])}\n")
        file.write("\n\n")
        file.write("[Peer]\n")
        file.write(f"PublicKey = {configuration['vpn']['keys']['public']}\n")
        file.write(f"PresharedKey = {configuration['vpn']['keys']['preshared']}\n")
        file.write(f"AllowedIPs = {allowed_ips}\n")
        file.write(f"PersistentKeepalive = 0\n")
        file.write(f"Endpoint = {configuration['vpn']['endpoint']}\n")
        file.flush()

    subprocess.call(["nmcli", "connection", "import", "type", "wireguard", "file", config_path])
    nmcli.connection.up(vpn_interface)
    return
        