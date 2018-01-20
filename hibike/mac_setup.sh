#!/bin/bash

if [[ "$(id -u)" == "0" ]]; then
    echo "Please run without sudo permissions."
    exit 1
fi

#curl "https://downloads.arduino.cc/arduino-1.8.1-linux64.tar.xz" | sudo tar -xJf - -C /opt

deps=("make" "gcc" "gcc-avr" "arduino-mk" "python3-pip")

if ! type make >/dev/null 2>&1 || ! type gcc >/dev/null 2>&1; then 
	echo "Install x-code on your mac!"
	exit 1
fi

if ! type avr-gcc >/dev/null 2>&1; then
	echo "Installing avr-gcc"
	brew tap osx-cross/avr
	brew install avr-gcc
fi

if [[ $(brew list | grep -c arduino-mk) == 0 ]]; then
	# add tap
	brew tap sudar/arduino-mk
	# to install the last stable release
	brew install arduino-mk
	# to install the development version
	brew install --HEAD arduino-mk
fi

if ! type pip3 >/dev/null 2>&1; then
	brew install python3
fi


if ! command -v pipenv &> /dev/null; then
    pip3 install pipenv
fi

pipenv install --dev
pip3 install serial
echo "All dependencies installed."
