#!/bin/bash

# Run this on a staff machine as root

# Enables wifi on the Beaglebone by forwarding all requests
# Network interface names may vary
iptables --table nat --append POSTROUTING --out-interface wlp2s0 -j MASQUERADE
iptables --append FORWARD --in-interface enp0s20f0u2 -j ACCEPT
echo 1 > /proc/sys/net/ipv4/ip_forward

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
cd $FRANKFURTER_DIR
scp scripts/install/start_tmux_job.sh ubuntu@192.168.7.2:~
echo 'Now ssh-ing into robot. Please run the start_tmux_job.sh script upon login.'
echo 'Yes, I know this is ghetto, but there are good reasons it works this way...seriously'
ssh ubuntu@192.168.7.2
