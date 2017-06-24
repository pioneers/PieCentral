#!/bin/bash

####################################################################################
# Instructions to install a specific update. Packaged in the tarballs used to
# distribute updates.
####################################################################################

HOME=/home/ubuntu
UPDATES_DIR=$HOME/updates
TMP_DIR=$UPDATES_DIR/tmp
PIECENTRAL_BACKUP_DIR=$HOME/PieCentral.backup

# Create new backup
sudo rm -rf $PIECENTRAL_BACKUP_DIR
cp -R $HOME/PieCentral $PIECENTRAL_BACKUP_DIR

# Check the tarball included `runtime` and `hibike`
if [ ! -d "$TMP_DIR/runtime" ] || [ ! -d "$TMP_DIR/hibike" ]; then
  exit 1
fi

# Replace `runtime` and `hibike`
sudo rm -rf $HOME/PieCentral/runtime
sudo rm -rf $HOME/PieCentral/hibike
mv $TMP_DIR/hibike $HOME/PieCentral
mv $TMP_DIR/runtime $HOME/PieCentral
cp $PIECENTRAL_BACKUP_DIR/runtime/studentCode.py $HOME/PieCentral/runtime
cp $PIECENTRAL_BACKUP_DIR/runtime/namedPeripherals.csv $HOME/PieCentral/runtime

# Copy executables
mv $TMP_DIR/resources/update.sh $HOME/bin
mv $TMP_DIR/resources/mac.py $HOME/bin
mv $TMP_DIR/resources/runtime.sh $HOME/bin

# Configure executable permissions
sudo chown ubuntu $HOME/bin/*
sudo chgrp ubuntu $HOME/bin/*
sudo chmod 755 $HOME/bin/*

# Copy bashrc with aliases
mv $TMP_DIR/resources/bashrc $HOME/.bashrc
sudo chmod 644 $HOME/.bashrc

# Update and enable services
sudo mv $TMP_DIR/resources/runtime.service /lib/systemd/system
sudo mv $TMP_DIR/resources/update.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/runtime.service
sudo chmod 644 /lib/systemd/system/update.service
sudo systemctl daemon-reload
sudo systemctl enable runtime.service
sudo systemctl enable update.service

ln -s $HOME/PieCentral/hibike/hibikeDevices.csv $HOME/PieCentral/runtime/hibikeDevices.csv

# Cleanup temporary directory
rm -rf $TMP_DIR
sync
