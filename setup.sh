#!/bin/bash

if [ "$(id -u)" != "0" ]; then
	echo "Please run with sudo permissions."
	exit 1
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


echo "All dependencies installed."