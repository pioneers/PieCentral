#!/bin/bash

# usb-fwd.sh -- Enable internet on a Beaglebone over USB with request forwarding

USER=ubuntu
HOST_IP_ADDR=192.168.7.1
DEV_IP_ADDR=192.168.7.2

ERROR="\e[1;31m"    # Bold red
WARNING="\e[1;33m"  # Bold yellow
SUCCESS="\e[1;32m"  # Bold green
CLEAR="\e[0m"

SSH_OPTIONS='-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -t'
IP_FORWARD_FILE=/proc/sys/net/ipv4/ip_forward

function print-help {
  echo 'Usage: ./usb-fwd.sh <command>'
  echo ''
  echo 'where the commands are: '
  echo '  * help                                    -- print this help text'
  echo '  * enable <host-wifi-iface> <device-iface> -- enable request forwarding'
  echo '  * disable                                 -- disable request forwarding'
  echo ''
  echo "Usage 'ifconfig' to identify interface names."
  echo ''
  echo 'This command may require sudo. We assume: '
  echo "  * the user is '$USER',"
  echo "  * this machine's IP address is '$HOST_IP_ADDR', and"
  echo "  * the Beaglebone's IP address is '$DEV_IP_ADDR'."
}

set -e

case $1 in
  enable)
    ssh $SSH_OPTIONS $USER@$DEV_IP_ADDR "sudo /sbin/route add default gw $HOST_IP_ADDR"
    iptables --table nat --append POSTROUTING --out-interface $2 -j MASQUERADE
    iptables --append FORWARD --in-interface $3 -j ACCEPT
    echo 1 > $IP_FORWARD_FILE
    ;;
  disable)
    ssh $SSH_OPTIONS $USER@$DEV_IP_ADDR "sudo /sbin/route delete default gw $HOST_IP_ADDR"
    echo 0 > $IP_FORWARD_FILE
    ;;
  help)
    print-help
    ;;
  *)
    echo -e $ERROR"No such command: '$1'.\n"$CLEAR
    print-help
esac
