#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
USER=ubuntu
IP=192.168.7.2

cd $FRANKFURTER_DIR

OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o"
OPTIONS="$OPTIONS IdentityFile=resources/frankfurter_vincent.pub"

CMD="cp /etc/ssh/sshd_config ~/sshd_config.bak"
CMD="$CMD && sudo mv ~/sshd_config /etc/ssh"
CMD="$CMD && rm ~/sshd_config"
CMD="$CMD && sudo restart ssh"

scp $OPTIONS resources/sshd_config $USER@$IP:~
ssh $OPTIONS $USER@$IP $CMD
