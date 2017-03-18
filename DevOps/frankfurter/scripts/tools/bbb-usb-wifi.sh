#!/bin/bash

# A hack to allow wifi on Beaglebones over USB during testing
# Modify the interface names below as needed, and run this as root
# Assumes SSH works on the remote machine (192.168.7.2)

ERROR="\e[1;31m"    # Bold red
WARNING="\e[1;33m"  # Bold yellow
SUCCESS="\e[1;32m"  # Bold green
CLEAR="\e[0m"

WIFI_INTERFACE=wlp2s0
BBB_INTERFACE=enp0s20f0u2

CMD="sudo /sbin/route add default gw 192.168.7.1"  # Need to undo this after setup
ssh -t ubuntu@192.168.7.2 $CMD

iptables --table nat --append POSTROUTING --out-interface $WIFI_INTERFACE -j MASQUERADE
iptables --append FORWARD --in-interface $BBB_INTERFACE -j ACCEPT
echo 1 > /proc/sys/net/ipv4/ip_forward
