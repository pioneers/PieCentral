#!/usr/bin/env python3

"""
mac
===
Print the MAC address of a network interface.
"""

from argparse import ArgumentParser
import fcntl
import socket
import struct
import sys


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


def main():
    description = 'print the MAC address of a network interface'
    parser = ArgumentParser(description=description)
    parser.add_argument('interface', help='the name of the network interface')
    args = parser.parse_args()

    try:
        mac_addr = get_mac_address(args.interface)
    except OSError as error:  # No such interface
        print('no such interface', file=sys.stderr)
    else:
        # 48 bits -> 12 hexadecimal characters (4 bits per character)
        mac_addr_hex = hex(mac_addr)[2:].rjust(12, '0')
        print(':'.join(mac_addr_hex[i : i+2] for i in range(0, 12, 2)))


if __name__ == '__main__':
    main()
