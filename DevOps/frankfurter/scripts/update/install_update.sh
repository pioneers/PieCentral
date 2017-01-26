#!/bin/bash

####################################################################################
# Instructions to install a specific update. Packaged in the tarballs used to
# distribute updates.
####################################################################################

HOME_DIR=/home/ubuntu
UPDATES_DIR=$HOME_DIR/updates
TMP_DIR=$UPDATES_DIR/tmp
PIECENTRAL_BACKUP_DIR=$HOME_DIR/PieCentral.backup

####################################################################################
# Update PieCentral:                                                                   #
####################################################################################
rm -rf $PIECENTRAL_BACKUP_DIR
cp -R $HOME_DIR/PieCentral $PIECENTRAL_BACKUP_DIR
rm -r $HOME_DIR/PieCentral/runtime
rm -r $HOME_DIR/PieCentral/hibike
mv $TMP_DIR/hibike $HOME_DIR/PieCentral
mv $TMP_DIR/runtime $HOME_DIR/PieCentral

ln -s $HOME_DIR/PieCentral/hibike/hibikeDevices.csv $HOME_DIR/PieCentral/runtime/testy/hibikeDevices.csv

####################################################################################
# Cleanup!                                                                         #
####################################################################################
rm -rf $TMP_DIR
sync
