#!/bin/bash

####################################################################################
# Robot-side script for installing an update. Takes the tarball given in an
# individual update, verifies that it is from us, then proceeds to defer to
# the individual update script to complete the process.
####################################################################################

UPDATES_DIR=/home/ubuntu/updates
TMP_DIR=$UPDATES_DIR/tmp

if ! ls $UPDATES_DIR/frankfurter-update-*.tar.gz 1> /dev/null 2>&1; then
  exit
fi
mkdir -p $TMP_DIR
cd $UPDATES_DIR

# Stop execution after first failure
set -e

# Extract the tarball
tar -xf $UPDATES_DIR/frankfurter-update-*.tar.gz -C $TMP_DIR --warning=no-timestamp
rm -rf $UPDATES_DIR/frankfurter-update*.tar.gz*

# an update tarball should have all of the instructions on how to install itself in its
# install_update.sh script, so we simply defer to it here.
bash $TMP_DIR/install_update.sh
