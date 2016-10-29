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

HOST=192.168.7.1  # Staff machine
/sbin/route add default gw $HOST  # Forwards all unresolved names to the host
                                  # Does not persist between reboots
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
timedatectl set-timezone America/Los_Angeles

# apt -y update && apt -y upgrade
# apt install -y $(cat dependencies.txt | tr "\n" " ")
# apt install -y man-db make build-essential gcc git htop curl memcached libevent-dev vim python3-dev python3-pip
# apt clean -y

# Install (most) apt-get packages ############################################################
sudo apt-get install -y make build-essential gcc git htop curl memcached libevent-dev vim

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
cd ~

# Install python, pip, and pip packages ######################################################
sudo apt-get -y upgrade
sudo apt-get install -y python python-dev python-pip
sudo pip install --upgrade -r $FRANKFURTER_DIR/resources/requirements.txt

# Install pygrizzly ##########################################################################
git clone https://github.com/pioneers/python-grizzly
cd python-grizzly
sudo python setup.py install
cd ..
sudo rm -rf python-grizzly

# download hibike and runtime ################################################################
git clone https://github.com/pioneers/daemon ~/daemon
git clone https://github.com/pioneers/hibike ~/hibike
ln -s ~/hibike/hibikeDevices.csv ~/daemon/runtime/hibikeDevices.csv

# set up things we need to update runtime and hibike #########################################
mkdir -p ~/updates
cp $FRANKFURTER_DIR/resources/update.sh ~/updates/

# copy .conf files into /etc/init so that hibike/dawn/runtime start on boot ##################
sudo cp $FRANKFURTER_DIR/resources/runtime.conf /etc/init
sudo cp $FRANKFURTER_DIR/resources/memcached.conf /etc/init
sudo rm /etc/init.d/memcached

#copy config files for grizzlies, memcached, and network interfaces
sudo cp $FRANKFURTER_DIR/resources/50-grizzlybear.rules /etc/udev/rules.d/
sudo cp $FRANKFURTER_DIR/resources/interfaces /etc/network/interfaces

echo "export PYTHONPATH=$HOME/hibike:$PYTHONPATH" >> ~/.bashrc  # .profile?

# stop the apache server from auto-starting
sudo rm -f /etc/init.d/apache2
