#!/bin/bash

# make_team_net -- Build a network configuration for a particular team.

source "$(git rev-parse --show-toplevel)/DevOps/frankfurter/scripts/tools/env"

build_dir="$tmp_dir/net-build"
mkdir -p "$build_dir"

read -e -p 'Enter the team number: ' team_number
if [[ -z $(echo "$team_number" | grep -E '^[0-9]+$') || ("$team_number" -gt 50) ]]; then
  echo -e $error"Invalid team number: '$team_number'"$clear
  echo "Team number must be integer between 0 and 50, inclusive."
  exit 1
fi
read -e -p 'Enter the team router password: ' router_psk

# Copy config file templates
cp "$frankfurter/resources/interfaces" "$build_dir"
cp "$frankfurter/resources/wpa_supplicant.conf" "$build_dir"

# Perform substitutions
sed -i "s/address 192.168.128.200/address 192.168.128.$(( team_number + 200 ))/" "$build_dir/interfaces"
sed -i "s/address 192.168.0.200/address 192.168.0.$(( team_number + 200 ))/" "$build_dir/interfaces"
sed -i "9s/ssid=\"\"/ssid=\"Team$team_number\"/" "$build_dir/wpa_supplicant.conf"
sed -i "10s/psk=\"\"/psk=\"$router_psk\"/" "$build_dir/wpa_supplicant.conf"

#Take in SD Card name and create directory to prepare for mounting process
CARDNAME=$1
mkdir /mnt/SD

#Unmount SD Card if already mounted
sudo umount $CARDNAME

#Mount SD Card
sudo mount -t vfat $CARDNAME /mnt/SD

#Move relevant files to SD Card
mv "$build_dir/interfaces" /mnt/SD/etc/network/
mv "$build_dir/wpa_supplicant.conf" /mnt/SD/etc/wpa_supplicant/

#Delete build_dir to avoid redundancy
rm -r "$build_dir"

#Unmount SD Card and remove the directory
sudo umount $CARDNAME
rm -r /mnt/SD
