#!/bin/bash

####################################################################################
# Instructions to install a specific update. Packaged in the tarballs used to
# distribute updates.
####################################################################################

HOME=/home/ubuntu
UPDATES_DIR=$HOME/updates
TMP_DIR=$UPDATES_DIR/tmp
PIECENTRAL_BACKUP_DIR=$HOME/PieCentral.backup

####################################################################################
# Update PieCentral:                                                                   #
####################################################################################
rm -rf $PIECENTRAL_BACKUP_DIR
cp -R $HOME/PieCentral $PIECENTRAL_BACKUP_DIR
rm -r $HOME/PieCentral/runtime
rm -r $HOME/PieCentral/hibike
mv $TMP_DIR/hibike $HOME/PieCentral
mv $TMP_DIR/runtime $HOME/PieCentral

sudo chown ubuntu -R $PIECENTRAL_BACKUP_DIR
sudo chgrp ubuntu -R $PIECENTRAL_BACKUP_DIR

ln -s $HOME/PieCentral/hibike/hibikeDevices.csv $HOME/PieCentral/runtime/testy/hibikeDevices.csv

####################################################################################
# Cleanup!                                                                         #
####################################################################################
rm -rf $TMP_DIR
sync
