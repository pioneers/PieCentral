#!/bin/bash

set -e
ip link
read -e -p "Enter the interface to accept from: " accept
read -e -p "Enter the interface to forward to: " forward
read -e -p "Enter the remote's IP address: " remote_ip
read -e -p "Enter the user to log into the remote as: " remote_user

host_ip=$(ip addr show "$accept" | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
echo "This machine's IP address on '$accept': $host_ip"

iptables -F
iptables -X

iptables -t nat -A POSTROUTING -o "$accept" -j MASQUERADE
iptables -A FORWARD -i "$accept" -o "$forward" -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i "$forward" -o "$accept" -j ACCEPT

iptables -t nat -A POSTROUTING -o "$forward" -j MASQUERADE
iptables -A FORWARD -i "$forward" -o "$accept" -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i "$accept" -o "$forward" -j ACCEPT

sysctl -w net.ipv4.ip_forward=1
ssh "$remote_user"@"$remote_ip" "sudo ip route add default via $host_ip"
