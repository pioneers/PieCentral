#!/bin/bash

# interfaces.sh -- An interactive script for configuring networking specific
#                  to each Beaglebone

USER=ubuntu
IP=192.168.7.2

FRANKFURTER_DIR="$(git rev-parse --show-toplevel)/DevOps/frankfurter"
BUILD_DIR="$FRANKFURTER_DIR/build"
mkdir -p $BUILD_DIR

ERROR="\e[1;31m"    # Bold red
WARNING="\e[1;33m"  # Bold yellow
SUCCESS="\e[1;32m"  # Bold green
CLEAR="\e[0m"

function read-team-number() {
  read -e -p 'Enter the team number: ' teamnumber
}

set -e

# Read user input
read-team-number
until [[ ! -z $(echo $teamnumber | grep -E '^[0-9]+$') ]]; do
  echo -e $WARNING"'$teamnumber' is not a valid team number."$CLEAR
  read-team-number
done
read -e -p 'Enter the team router password: ' teampsk

# Copy template files
cp $FRANKFURTER_DIR/resources/interfaces $BUILD_DIR
cp $FRANKFURTER_DIR/resources/wpa_supplicant.conf $BUILD_DIR

# Perform substitutions
sed -i "s/<field-addr>/$((teamnumber + 200))/" $BUILD_DIR/interfaces
sed -i "s/<team-addr>/$((teamnumber + 200))/" $BUILD_DIR/interfaces
sed -i "s/<team-ssid>/Team$teamnumber/" $BUILD_DIR/wpa_supplicant.conf
sed -i "s/<team-psk>/$teampsk/" $BUILD_DIR/wpa_supplicant.conf

# Copy and move files
scp $BUILD_DIR/interfaces $BUILD_DIR/wpa_supplicant.conf $USER@$IP:~
CMD='sudo mv ~/interfaces /etc/network/interfaces'
CMD="$CMD && sudo mv ~/wpa_supplicant.conf /etc/wpa_supplicant"
ssh -t $USER@$IP $CMD

# Clean up
rm $BUILD_DIR/interfaces
rm $BUILD_DIR/wpa_supplicant.conf
