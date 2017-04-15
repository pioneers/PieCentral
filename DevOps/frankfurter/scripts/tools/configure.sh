#!/bin/bash

# configure.sh -- Team-specific configuration

SCRIPTS_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter/scripts

cd $SCRIPTS_DIR/tools
./interfaces.sh
cd $SCRIPTS_DIR/update
./deploy_update.sh
cd $SCRIPTS_DIR/tools
./usb-fix.sh
