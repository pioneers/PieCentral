#!/bin/bash
sudo echo 'nameserver 8.8.8.8' >> /etc/resolvconf/resolv.conf.d/base
sudo systemctl restart resolvconf.service
sudo rm /etc/resolv.conf
sudo ln -s /run/resolvconf/resolv.conf /etc/resolv.conf
cd $HOME
cd wifi-driver-src
make clean
make
sudo make install
