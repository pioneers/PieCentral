#!/bin/bash

####################################################################################
# Robot-side script for installing an update. Unpacks the tarball given in an
# individual update, then proceeds to defer to the individual update script to
# complete the process.
####################################################################################

# We cannot assume this runs as `ubuntu` (e.g. `systemd` running as `root`)
HOME=/home/ubuntu
UPDATES_DIR=$HOME/updates
TMP_DIR=$UPDATES_DIR/tmp

if ! ls $UPDATES_DIR/frankfurter-update-*.tar.gz 1> /dev/null 2>&1; then
  exit
fi

# Stop execution after first failure
set -e

sudo -u ubuntu mkdir -p $TMP_DIR
cd $UPDATES_DIR

# Extract the tarball
sudo -u ubuntu tar -xf $UPDATES_DIR/frankfurter-update-*.tar.gz -C $TMP_DIR --warning=no-timestamp

# an update tarball should have all of the instructions on how to install itself in its
# install_update.sh script, so we simply defer to it here.
sudo -u ubuntu bash $TMP_DIR/install_update.sh

rm -f $UPDATES_DIR/*.tar.gz && rm -rf $UPDATES_DIR/tmp
