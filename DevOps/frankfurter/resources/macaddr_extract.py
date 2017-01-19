import mac.py

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
