#!/bin/sh

echo 'Starting frankfurter installation ...'
source $(git rev-parse --show-toplevel)/DevOps/frankfurter/scripts/tools/env.sh
cd $TMP_DIR
git clone https://github.com/xtknight/mt7610u-linksys-ae6000-wifi-fixes.git wifi-driver-src
scp -r wifi-driver-src $USER@IP:~

CMD="echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
CMD="$CMD && cd ~/wifi-driver-src && make clean && make && sudo make install"
CMD="$CMD && echo 'mt7610u_sta' >> /etc/modules && sudo reboot"
ssh $USER@$IP $CMD
rm -rf wifi-driver-src
