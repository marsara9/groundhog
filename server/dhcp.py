import socket
import struct
import subprocess

class DHCP():

    __process = None
    
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
    