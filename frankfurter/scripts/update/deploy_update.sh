#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/frankfurter
IP=192.168.13.100

cd $FRANKFURTER_DIR

if ! ls build/frankfurter-update-* 1> /dev/null 2>&1; then
    make create_update
fi


ssh ubuntu@$IP 'rm -rf ~/updates/*.tar.gz* && rm -rf ~/updates/temp'
scp build/* ubuntu@$IP:~/updates/
ssh ubuntu@$IP 'sudo restart runtime'
