import socket
import struct
import subprocess

class DHCP():

    __process = None

    def get_config(conf: str):
        dnsmasq = {}
        for line in conf.split("\n"):
            entry = line.split("=")
            if entry[0] not in dnsmasq:
                if len(entry) == 2:
                    items = entry[1].split(",")
                    if items[0].isdigit():
                        dnsmasq[entry[0]] = {
                            items[0]: items[1:]
                        }
                    elif len(items) > 1:
                        dnsmasq[entry[0]] = items[:]
                    else:
                        dnsmasq[entry[0]] = entry[1]
                else:
                    dnsmasq[line] = True
            elif len(entry) == 2:
                items = entry[1].split(",")
                if items[0].isdigit():
                    dnsmasq[entry[0]][items[0]] = items[1:]
                elif len(items) > 1:
                    dnsmasq[entry[0]] = [
                        dnsmasq[entry[0]],
                        items[:]
                    ]
                else:
                    dnsmasq[entry[0]] = [
                        dnsmasq[entry[0]],
                        entry[1]
                    ]
        return dnsmasq
        
    def __ip_to_long(ip):
        return struct.unpack("!L", socket.inet_aton(ip))[0]
        
    def __long_to_ip(addr):
        return socket.inet_ntoa(struct.pack('!L', addr))
        
    def get_subnet(ip : str, netmask : str):
        return DHCP.__long_to_ip(DHCP.__ip_to_long(ip) & DHCP.__ip_to_long(netmask))

    def get_subnet_cidr(ip : str, netmask : str):
        return f"{DHCP.get_subnet(ip, netmask)}/{(bin(DHCP.__ip_to_long(netmask))[2:]).count('1')}"

    def get_range(subnet : str, max_clients : int, reserved_clients : int):
        start = DHCP.__ip_to_long(subnet) | reserved_clients + 1
        end = DHCP.__ip_to_long(subnet) | reserved_clients + 1 + max_clients
        return (start, end)
        
    def restart(self, config_path : str):
        if self.__process:
            self.__process.terminate()
            self.__process.wait()

        self.__process = subprocess.Popen([
            "dnsmasq",
            "-C",
            config_path
        ])
    