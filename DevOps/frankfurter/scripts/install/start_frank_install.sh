#!/bin/bash

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/frankfurter
cd $FRANKFURTER_DIR
scp scripts/install/start_tmux_job.sh ubuntu@192.168.7.2:~
echo 'Now ssh-ing into robot. Please run the start_tmux_job.sh script upon login.'
echo 'Yes, I know this is ghetto, but there are good reasons it works this way...seriously'
ssh ubuntu@192.168.7.2
