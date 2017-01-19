import mac
from argparse import ArgumentParser
import sys

description = 'print the MAC address of a network interface'
parser = ArgumentParser(description=description)
parser.add_argument('interface', help='the name of the network interface')
args = parser.parse_args()

try:
    mac_addr = mac.get_mac_address(args.interface)
except OSError as error:  # No such interface
    print('no such interface', file=sys.stderr)
else:
    # 48 bits -> 12 hexadecimal characters (4 bits per character)
    mac_addr_hex = hex(mac_addr)[2:].rjust(12, '0')
    mac=(':'.join(mac_addr_hex[i : i+2] for i in range(0, 12, 2)))
    file_dir = (os.path.dirname(os.path.realpath(__file__)))
    team_number = input('What is the team number?')
    direc = os.listdir()
    check = []
    for i in direc:
        if 'mac_addresses.txt' == i:
            check.append(1)
    if len(check) == 0:
        with open(file_dir+'/mac_addresses.txt', 'a') as text_file:
            text_file.write('team_number, mac_number')
            text_file.write('\n')
    with open(file_dir+'/mac_addresses.txt', 'a') as text_file:
        text_file.write(team_number + ', ' + str(mac))
        text_file.write('\n')
