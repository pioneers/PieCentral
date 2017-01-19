#!/usr/bin/env python3

"""
mac
===
Print the MAC address of a network interface.
"""

import fcntl
import socket
import struct

def get_mac_address(interface):
    """
    Get the MAC address of a networked device as a 48-bit integer.

    References:
      * https://stackoverflow.com/questions/159137/getting-mac-address
    """
    ifname_as_struct = struct.pack('256s', interface[:15].encode('utf-8'))
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(skt.fileno(), 0x8927, ifname_as_struct)
    return int.from_bytes(info[18:24], byteorder='big')
