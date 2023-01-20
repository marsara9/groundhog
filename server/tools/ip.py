import socket
import struct
import validators

def ip_to_long(ip):
    """
    Converts a IP address to a number.

    Example: 192.168.1.1 -> 0xc0a80101
    """
    return struct.unpack("!L", socket.inet_aton(ip))[0]
        
def long_to_ip(addr):
    """
    Converts a number to an IP address

    Example: 0xc0a80101 -> 192.168.1.1
    """
    return socket.inet_ntoa(struct.pack('!L', addr))

def get_subnet_ip_cidr(ip : str):
    """
    Given a CIDR formatted IP address return subnet for that same IP.

    Example: 192.168.1.1/24 -> 192.168.1.0
    """
    validators.ipv4_cidr(ip)

    (ip, prefix) = tuple(map(str, ip.split("/")))

    netmask = 0xFFFFFFFF << (32-int(prefix))

    return long_to_ip(ip_to_long(ip) & netmask)
    
def get_range(
    subnet_cidr : str, 
    max_clients : int, 
    reserved_clients : int = 1
) -> tuple(str,str):
    """
    Given a subnet ip (example: 192.168.1.0/24) this will return the min and max 
    IP addresses in the given subnet that has the specified number of clients.

    Keyword arguments:
        subnet -- The subnet to work from.

        max_clients -- The number of IP addresses that should be within the range.

        reserved_clients -- The number IP addresses to reserve at the begining of the subnet.
    """

    validators.ipv4_cidr(subnet_cidr)

    (subnet, prefix) = tuple(map(str, subnet_cidr.split("/")))

    netmask = 0xFFFFFFFF << (32-int(prefix))

    if netmask & (reserved_clients + 1 + max_clients) != 0:
        raise Exception("max_clients + reserved_clients is greater than the subnet can support.")

    start = ip_to_long(subnet) | reserved_clients + 1
    end = ip_to_long(subnet) | reserved_clients + 1 + max_clients

    return (start, end)