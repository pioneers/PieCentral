#!/bin/bash

PIECENTRAL_REPO=$(git rev-parse --show-toplevel)
RUNTIME_DIR=$PIECENTRAL_REPO/runtime
HIBIKE_DIR=$PIECENTRAL_REPO/hibike
FRANKFURTER_DIR=$PIECENTRAL_REPO/DevOps/frankfurter

USER=ubuntu
IP=192.168.7.2
if [ -d /tmp ]; then
  TMP_DIR=/tmp
else
  TMP_DIR=$(pwd)
fi

ERROR="\e[1;31m"    # Bold red
WARNING="\e[1;33m"  # Bold yellow
SUCCESS="\e[1;32m"  # Bold green
CLEAR="\e[0m"

alias sudo='sudo -H'
alias ssh='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -t'
