#!/bin/bash

####################################################################################
# Instructions to install a specific update. Packaged in the tarballs used to
# distribute updates.
####################################################################################

HOME_DIR=/home/ubuntu
UPDATES_DIR=$HOME_DIR/updates
TEMP_DIR=$UPDATES_DIR/temp

####################################################################################
# Update PieCentral:                                                                   #
####################################################################################
mv $HOME_DIR/PieCentral $HOME_DIR/PieCentral_old
rm -r $HOME_DIR/PieCentral/runtime
rm -r $HOME_DIR/PieCentral/hibike
mv $TEMP_DIR/hibike $HOME_DIR/PieCentral
mv $TEMP_DIR/runtime $HOME_DIR/PieCentral

ln -s $HOME_DIR/PieCentral/hibike/hibikeDevices.csv $HOME_DIR/PieCentral/runtime/testy/hibikeDevices.csv

####################################################################################
# Cleanup!                                                                         #
####################################################################################
rm -rf $TEMP_DIR
sync
