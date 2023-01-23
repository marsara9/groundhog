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

def get_subnet_prefix(ip : str) -> int:
    """
    Returns the prefix of a given CIDR notation IP address.

    Example: 192.168.1.1/24 -> 24
    """
    validators.ipv4_cidr(ip)

    return int(ip.split("/")[1])

def get_ip_from_subnet(subnet_cidr : str, value : int) -> str:
    """
    Takes a given subnet and value and combines them to generate a new IP address.

    For example, if the subnet is to set to `192.168.1.0/24` and the value is `3`, this
    method will return `192.168.1.3`.  However if you suppy a value that is greater
    than what can fit in the subnet, then an exception is thrown.  i.e. `192.168.1.0/24`
    and `260` would produce `192.168.2.5` which is outside of the subnet specified by
    `/24`, but `192.168.0.0/16` and `260` would work.
    """
    validators.ipv4_cidr(subnet_cidr)

    (subnet, prefix) = tuple(map(str, subnet_cidr.split("/")))
    netmask = 0xFFFFFFFF << (32-int(prefix))

    if ~netmask & value != value:
        raise Exception("IP is out of subnet range")

    return long_to_ip(ip_to_long(subnet) + value)
    
def get_range(
    subnet_cidr : str, 
    max_clients : int, 
    reserved_clients : int = 1
) -> tuple[str,str]:
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

    start = long_to_ip(ip_to_long(subnet) | reserved_clients + 1)
    end = long_to_ip(ip_to_long(subnet) | reserved_clients + 1 + max_clients)

    return (start, end)