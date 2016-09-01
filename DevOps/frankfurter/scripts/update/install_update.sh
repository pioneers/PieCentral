#!/bin/bash

####################################################################################
# Instructions to install a specific update. Packaged in the tarballs used to
# distribute updates.
####################################################################################

HOME_DIR=/home/ubuntu
UPDATES_DIR=$HOME_DIR/updates
RUNTIME_DIR=$HOME_DIR/daemon/runtime
TEMP_DIR=$UPDATES_DIR/temp

####################################################################################
# Update hibike:                                                                   #
####################################################################################
mv $TEMP_DIR/hibike $HOME_DIR/hibike_new
rm -rf $HOME_DIR/hibike_old
mv $HOME_DIR/hibike $HOME_DIR/hibike_old
mv $HOME_DIR/hibike_new $HOME_DIR/hibike

####################################################################################
# Update runtime:                                                                  #
# This is a bit more involved as we need to avoid deleting student code.           #
####################################################################################
cp -r $RUNTIME_DIR/student_code $TEMP_DIR
mv $TEMP_DIR/daemon $HOME_DIR/daemon_new
rm -rf $HOME_DIR/daemon_old
mv $HOME_DIR/daemon $HOME_DIR/daemon_old
mv $HOME_DIR/daemon_new $HOME_DIR/daemon
cp -r $TEMP_DIR/student_code $RUNTIME_DIR

ln -s $HOME_DIR/hibike/hibikeDevices.csv $RUNTIME_DIR/hibikeDevices.csv

# SO CONFUSED. this makes no sense to me. online documentation says this should be
# set to 600 and after a login things are set to 600, but the initial login doesn't
# work unless these permissions are initially set to 644. I'm guessing the sshd
# process is doing something here, but for now I'm not quite sure what.
chmod 700 $HOME_DIR/.ssh
chmod 644 $HOME_DIR/.ssh/authorized_keys
chown ubuntu $HOME_DIR/.ssh
chown ubuntu $HOME_DIR/.ssh/authorized_keys

####################################################################################
# Cleanup!                                                                         #
####################################################################################
rm -rf $TEMP_DIR
sync
