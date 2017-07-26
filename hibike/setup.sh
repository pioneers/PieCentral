#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "Please run with sudo permissions."
    exit 1
fi

cp utils/flash /etc/bash_completion.d/flash.sh
echo "Setup Tab-complete"
echo "Please restart your terminals"

sudo usermod -a -G dialout "$(whoami)"

if [ $# -eq 1 ] && [ "$(echo "$1" | grep -c -i -E ".*arduino.*(\.tar|\.tar\.xz)")" != 0 ]; then
    echo "Extracting Arduino file..."
    tar xf "$1" -C /opt
    echo "Successfully installed Arduino 1.8.1 into /opt"
elif [ $# -eq 1 ]; then
    echo "You must download Arduino 1.8.1 from https://www.arduino.cc/en/Main/Software"
else
    echo "To update to Arduino 1.8.1: First command line argument as file path to .tar (or .tar.xz)"
fi

if [ "$(dpkg-query -W -f='${Status}' make 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install make
fi

if [ "$(dpkg-query -W -f='${Status}' gcc 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install gcc
fi

if [ "$(dpkg-query -W -f='${Status}' gcc-avr 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install gcc-avr
fi

if [ "$(dpkg-query -W -f='${Status}' arduino 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install arduino
fi

if [ "$(dpkg-query -W -f='${Status}' arduino-core 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install arduino-core
fi

if [ "$(dpkg-query -W -f='${Status}' arduino-mk 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install arduino-mk
fi

if [ "$(dpkg-query -W -f='${Status}' avr-libc 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install avr-libc
fi

if [ "$(dpkg-query -W -f='${Status}' python3-pip 2>/dev/null | grep -c "ok installed")" != 1 ]; then
    apt-get --assume-yes install python3-pip
fi

pip3 install -r requirements.txt

echo "All dependencies installed."
