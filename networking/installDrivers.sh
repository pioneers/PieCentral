#!/bin/bash

sudo apt-get update
git clone https://github.com/xtknight/mt7610u-linksys-ae6000-wifi-fixes.git drivers
cd drivers
make clean
sudo apt-get install build-essential linux-headers-$(uname -r)
make
sudo make install
