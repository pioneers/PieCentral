#!/bin/bash

##############################################################################################
# Initially configures a frank robot, assuming the robot has been freshly flashed with       #
# Ubuntu. Note that this script will not be used in production as it is far too slow, and we #
# will instead be flashing the eMMC of a single "master" frank onto each robot for the sake  #
# of speed. This script exists for the purpose of having an easily maintainable way to bring #
# up a master frank. We assume this master frank is set up while tethered to a computer with #
# internet sharing.                                                                          #
#                                                                                            #
# Network config, along with the setup of a few miscellaneous settings (that will need to be #
# changed from robot to robot) will be handled by a separate script run on a robot-by-robot  #
# basis.                                                                                     #
##############################################################################################

HOME=/home/ubuntu

# Configure date and time
sudo timedatectl set-timezone America/Los_Angeles

# Disable default Apache server (permanently)
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl daemon-reload

alias sudo='sudo -H'

# Install apt packages
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y man-db make build-essential gcc git vim tmux htop curl memcached libevent-dev unzip systemd systemd-sysv linux-headers-$(uname -r)
sudo apt install -y python3 python3-dev python3-pip  # Python dependencies
sudo apt clean -y
sudo apt autoremove -y

# Install Python packages
sudo pip3 install -r $HOME/PieCentral/runtime/requirements.txt
sudo pip3 install -U pyserial pyyaml python-memcached flask flask-socketio eventlet pyusb protobuf

# Install wireless dongle driver
cd $HOME
git clone https://github.com/xtknight/mt7610u-linksys-ae6000-wifi-fixes.git drivers
cd drivers
make clean
make
sudo make install
echo 'mt7610u_sta' | sudo tee --append /etc/modules

cd $HOME/PieCentral
PIECENTRAL_DIR=$(git rev-parse --show-toplevel)
FRANKFURTER_DIR=$PIECENTRAL_DIR/DevOps/frankfurter

if [ ! -f $PIECENTRAL_DIR/runtime/hibikeDevices.csv ]; then
  ln -s $PIECENTRAL_DIR/hibike/hibikeDevices.csv $PIECENTRAL_DIR/runtime/hibikeDevices.csv
fi

# Set up directories needed by other projects
mkdir -p $HOME/updates
mkdir -p $HOME/bin

# Copy executables
cp $FRANKFURTER_DIR/resources/update.sh $HOME/bin
cp $FRANKFURTER_DIR/resources/mac.py $HOME/bin
cp $FRANKFURTER_DIR/resources/runtime.sh $HOME/bin

# Configure executable permissions
sudo chown ubuntu $HOME/bin/*
sudo chgrp ubuntu $HOME/bin/*
sudo chmod 755 $HOME/bin/*

# Create and enable the `runtime` and `update` systemd services
sudo cp $FRANKFURTER_DIR/resources/runtime.service /lib/systemd/system
sudo cp $FRANKFURTER_DIR/resources/update.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/runtime.service
sudo chmod 644 /lib/systemd/system/update.service
sudo systemctl daemon-reload
sudo systemctl enable update.service
sudo systemctl enable runtime.service
sudo systemctl start runtime.service

# Copy config files for memcached and network interfaces
sudo cp $FRANKFURTER_DIR/resources/memcached.conf /etc
sudo cp $FRANKFURTER_DIR/resources/interfaces /etc/network/interfaces

cp $FRANKFURTER_DIR/resources/bashrc $HOME/.bashrc

sudo /sbin/route delete default gw 192.168.7.1
sudo systemctl restart networking.service
