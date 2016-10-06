#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
IP=192.168.13.100

cd $FRANKFURTER_DIR

if ! ls build/frankfurter-update-* 1> /dev/null 2>&1; then
    make create_update
fi

# Disable host fingerprinting
OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
ssh $OPTIONS ubuntu@$IP 'rm -rf ~/updates/*.tar.gz* && rm -rf ~/updates/temp'
scp $OPTIONS build/* ubuntu@$IP:~/updates/
ssh $OPTIONS ubuntu@$IP 'sudo restart runtime'
