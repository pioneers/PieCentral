#!/usr/bin/env python3

"""
interfaces -- Create and copy a custom network interface
"""

import os
import paramiko
from scp import SCPClient

HOST = '192.168.7.2'
USERNAME, PASSWORD = 'ubuntu', 'temppwd'
TMP_FILE_PATH = '/tmp/interfaces'


def read_user_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print('Not a number.')


def build_custom_config(team_number, password):
    with open('interfaces') as network_config_file:
        for line in network_config_file:
            if 'router_name' in line:
                line = line.replace('router_name', 'Team{0}'.format(team_number))
            if 'router_password' in line:
                line = line.replace('router_password', str(password))
            yield line[:-1]  # Take off the newline
            if 'wpa-psk' in line:
                indent = ' '*4
                yield indent + 'address 192.168.0.{0}'.format(200 + team_number)
                yield indent + 'netmask 255.255.255.0'
                yield indent + 'network 192.168.0.0'
                yield indent + 'gateway 192.168.0.1'


def write_tmp_file(lines):
    with open(TMP_FILE_PATH, 'w+') as tmp_file:
        print('\n'.join(lines), file=tmp_file)


def copy_network_config_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, password=PASSWORD)

    with SCPClient(ssh.get_transport()) as scp:
        scp.put(TMP_FILE_PATH, '/tmp/interfaces')

    ssh.exec_command('sudo mv /tmp/interfaces /etc/network')
    ssh.exec_command('sudo chown root /etc/network/interfaces')
    ssh.exec_command('sudo chgrp root /etc/network/interfaces')

    ssh.close()


def delete_tmp_file():
    os.remove(TMP_FILE_PATH)


def main():
    team_number = read_user_input('Please enter the team number: ')
    password = read_user_input('Please enter the router password: ')
    lines = build_custom_config(team_number, password)
    write_tmp_file(lines)
    copy_network_config_file()
    delete_tmp_file()


if __name__ == '__main__':
    main()
