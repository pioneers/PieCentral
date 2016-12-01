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
sudo service apache2 stop
sudo systemctl disable apache2
sudo systemctl daemon-reload

# Install apt packages
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y autoconf automake libtool g++  # For compiling `protoc` from source
sudo apt install -y man-db make build-essential gcc git vim tmux htop curl memcached libevent-dev unzip
sudo apt install -y python3 python3-dev python3-pip  # Python dependencies
sudo apt clean -y

# Install Python packages
sudo pip3 install -U pyserial pyyaml python-memcached flask flask-socketio eventlet pyusb protobuf

# Get PieCentral
cd $HOME
if [ ! -d PieCentral ]; then
  git clone https://github.com/pioneers/PieCentral.git
fi
cd PieCentral

PIECENTRAL_DIR=$(git rev-parse --show-toplevel)
FRANKFURTER_DIR=$PIECENTRAL_DIR/DevOps/frankfurter

if [ ! -f $PIECENTRAL_DIR/runtime/hibikeDevices.csv ]; then
  ln -s $PIECENTRAL_DIR/hibike/hibikeDevices.csv $PIECENTRAL_DIR/runtime/hibikeDevices.csv
fi

# Set up things we need to update runtime and hibike
mkdir -p $HOME/updates
cp $FRANKFURTER_DIR/resources/update.sh $HOME/updates/

# copy .conf files into /etc/init so that hibike/dawn/runtime start on boot
# cp $FRANKFURTER_DIR/resources/memcached.conf /etc
# cp $FRANKFURTER_DIR/resources/runtime /etc/init.d
# update-rc.d runtime defaults

# sudo cp $FRANKFURTER_DIR/resources/runtime.conf /etc/init
# sudo cp $FRANKFURTER_DIR/resources/memcached.conf /etc/init
# sudo rm /etc/init.d/memcached

# copy config files for grizzlies, memcached, and network interfaces
sudo cp $FRANKFURTER_DIR/resources/interfaces /etc/network/interfaces

echo "export PYTHONPATH=$HOME/hibike:$PYTHONPATH" >> $HOME/.bashrc  # .profile?
