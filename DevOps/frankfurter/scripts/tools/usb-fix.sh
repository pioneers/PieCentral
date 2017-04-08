#!/bin/bash

USER=ubuntu
IP=192.168.7.2
DEV_TREE_SRC_DIR=/opt/source/dtb-4.4-ti
DEV_TREE_FILE=$DEV_TREE_SRC_DIR/src/arm/am335x-bone-common.dtsi

CMD="sudo sed -i '210s/peripheral/host/' $DEV_TREE_FILE && cd $DEV_TREE_SRC_DIR"
CMD="$CMD && sudo make clean && sudo make && sudo make install && sudo reboot"
ssh -t $USER@$IP $CMD
