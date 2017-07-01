#!/bin/bash

# update.sh -- Robot-side script for installing an update
#
# Unpacks a zipped tarball and calls an included script to perform the update.

USER=ubuntu
HOME=/home/$USER
UPDATES_DIR=$HOME/updates
TMP_DIR=$UPDATES_DIR/tmp

# Stop execution after first failure
set -e

echo 'Starting update: scanning for files ...'

for filename in $(ls -At $UPDATES_DIR); do
  if [[ ! -z $(file $UPDATES_DIR/$filename | grep 'gzip compressed data') ]]; then
    echo "Extracting $UPDATES_DIR/$filename ..."
    sudo -u $USER mkdir -p $TMP_DIR
    sudo -u $USER tar -xf $UPDATES_DIR/$filename -C $TMP_DIR --warning=no-timestamp

    installer=$TMP_DIR/install_update.sh
    if [ -e $installer ]; then
      echo 'Running install script ...'
      sudo -u $USER bash $installer
    else
      echo "Error: expected, but could not find '$installer'"
    fi

    echo 'Cleaning up temporary directory ...'
    rm -f $UPDATES_DIR/$filename
    rm -rf $TMP_DIR

    break
  fi
done

echo 'Done.'
