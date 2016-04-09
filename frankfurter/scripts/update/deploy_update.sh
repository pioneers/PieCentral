#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/frankfurter
cd $FRANKFURTER_DIR

if ! ls build/frankfurter-update-* 1> /dev/null 2>&1; then
    make create_update
fi

scp build/* ubuntu@192.168.13.100:~/updates/
ssh ubuntu@192.168.13.100 'sudo restart runtime'
